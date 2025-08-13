from collections import defaultdict

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext as _
from django_rq import get_queue

from netbox.config import get_config
from netbox.constants import RQ_QUEUE_DEFAULT
from utilities.rqworker import get_rq_retry
from extras.choices import EventRuleActionChoices
from extras.models import EventRule


def process_event_rules(event_rules, object_type, event_type, data, username=None, snapshots=None, request_id=None):
    if username:
        user = get_user_model().objects.get(username=username)
    else:
        user = None

    for event_rule in event_rules:

        # Evaluate event rule conditions (if any)
        if not event_rule.eval_conditions(data):
            continue

        # Compile event data
        event_data = event_rule.action_data or {}
        event_data.update(data)

        # Webhooks
        if event_rule.action_type == EventRuleActionChoices.WEBHOOK:

            # Select the appropriate RQ queue
            queue_name = get_config().QUEUE_MAPPINGS.get('webhook', RQ_QUEUE_DEFAULT)
            rq_queue = get_queue(queue_name)

            # Compile the task parameters
            params = {
                "event_rule": event_rule,
                "model_name": object_type.model,
                "event_type": event_type,
                "data": event_data,
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
            event_data['snapshots'] = snapshots
            event_data['event'] = event_type
            event_data['username'] = username

            # Enqueue a Job to record the script's execution
            from extras.jobs import ScriptJob
            ScriptJob.enqueue(
                instance=event_rule.action_object,
                name=script.name,
                user=user,
                data=event_data
            )

        # Notification groups
        elif event_rule.action_type == EventRuleActionChoices.NOTIFICATION:
            # Bulk-create notifications for all members of the notification group
            event_rule.action_object.notify(
                object_type=object_type,
                object_id=event_data['id'],
                object_repr=event_data.get('display'),
                event_type=event_type
            )

        else:
            raise ValueError(_("Unknown action type for an event rule: {action_type}").format(
                action_type=event_rule.action_type
            ))


def process_event_queue(events):
    """
    Flush a list of object representation to RQ for EventRule processing.
    """
    events_cache = defaultdict(dict)

    for event in events:
        event_type = event['event_type']
        object_type = event['object_type']

        # Cache applicable Event Rules
        if object_type not in events_cache[event_type]:
            events_cache[event_type][object_type] = EventRule.objects.filter(
                event_types__contains=[event['event_type']],
                object_types=object_type,
                enabled=True
            )
        event_rules = events_cache[event_type][object_type]

        process_event_rules(
            event_rules=event_rules,
            object_type=object_type,
            event_type=event['event_type'],
            data=event['data'],
            username=event['username'],
            snapshots=event['snapshots'],
            request_id=event['request_id']
        )
