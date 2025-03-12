from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext as _
from django_rq import get_queue

from core.models import Job
from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT
from utilities.rqworker import get_rq_retry
from extras.choices import EventRuleActionChoices, ObjectChangeActionChoices
from extras.models import EventRule


def process_event_rules(event_rules, model_name, event, data, username=None, snapshots=None, request_id=None):
    if username:
        user = get_user_model().objects.get(username=username)
    else:
        user = None

    for event_rule in event_rules:

        # Evaluate event rule conditions (if any)
        if not event_rule.eval_conditions(data):
            continue

        # Webhooks
        if event_rule.action_type == EventRuleActionChoices.WEBHOOK:

            # Select the appropriate RQ queue
            queue_name = get_config().QUEUE_MAPPINGS.get('webhook', RQ_QUEUE_DEFAULT)
            rq_queue = get_queue(queue_name)

            # Compile the task parameters
            params = {
                "event_rule": event_rule,
                "model_name": model_name,
                "event": event,
                "data": data,
                "snapshots": snapshots,
                "timestamp": timezone.now().isoformat(),
                "username": username,
                "retry": get_rq_retry()
            }
            if snapshots:
                params["snapshots"] = snapshots
            if request_id:
                params["request_id"] = request_id

            # Enqueue the task
            rq_queue.enqueue(
                "extras.webhooks.send_webhook",
                **params
            )

        # Scripts
        elif event_rule.action_type == EventRuleActionChoices.SCRIPT:
            # Resolve the script from action parameters
            script = event_rule.action_object.python_class()
            # a little trick for https://github.com/netbox-community/netbox/issues/14896
            data['snapshots'] = snapshots
            data['event'] = event
            data['username'] = username

            # Enqueue a Job to record the script's execution
            Job.enqueue(
                "extras.scripts.run_script",
                instance=event_rule.action_object,
                name=script.name,
                user=user,
                data=data
            )

        else:
            raise ValueError(_("Unknown action type for an event rule: {action_type}").format(
                action_type=event_rule.action_type
            ))


def process_event_queue(events):
    """
    Flush a list of object representation to RQ for EventRule processing.
    """
    events_cache = {
        'type_create': {},
        'type_update': {},
        'type_delete': {},
    }

    for data in events:
        action_flag = {
            ObjectChangeActionChoices.ACTION_CREATE: 'type_create',
            ObjectChangeActionChoices.ACTION_UPDATE: 'type_update',
            ObjectChangeActionChoices.ACTION_DELETE: 'type_delete',
        }[data['event']]
        content_type = data['content_type']

        # Cache applicable Event Rules
        if content_type not in events_cache[action_flag]:
            events_cache[action_flag][content_type] = EventRule.objects.filter(
                **{action_flag: True},
                object_types=content_type,
                enabled=True
            )
        event_rules = events_cache[action_flag][content_type]

        process_event_rules(
            event_rules, content_type.model, data['event'], data['data'], data['username'],
            snapshots=data['snapshots'], request_id=data['request_id']
        )
