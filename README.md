# NetBox Scripthelper

Collections of utilities for Netbox custom scripts.

# Install
The plugin is available as a [Python package](https://pypi.org/project/netbox-scripthelper/) in pypi and can be installed with pip
```
python -m pip install netbox-scripthelper
```

Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:
```
PLUGINS = ['netbox_scripthelper']
```

To ensure the plugin is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the NetBox root directory (alongside `requirements.txt`) and append the `netbox-scripthelper` package:

```no-highlight
echo netbox-scripthelper >> local_requirements.txt
```

# Helpers

## DynamicChoiceField

Inspired by https://github.com/netbox-community/netbox/discussions/9326.
This field allows you to select available models (such as VLAN, Prefix, Address) in the NetBox Script interface.

Supported locations:

* `/api/plugins/scripthelper/ip-ranges/{{iprange}}/available-ips/` - returns list of available IP addresses from the IP range `{{iprange}}`;
* `/api/plugins/scripthelper/prefixes/{{prefix}}/available-prefixes/` - returns list of available prefixes from the parent prefix `{{prefix}}`;
* `/api/plugins/scripthelper/prefixes/{{prefix}}/available-ips/` - returns list of available IP addresses from the prefix `{{prefix}}`;
* `/api/plugins/scripthelper/prefixes/{{prefix}}/child-ips/` - returns list of child IP addresses from the prefix `{{prefix}}`;
* `/api/plugins/scripthelper/vlan-groups/{{vlan_group}}/available-vlans/` - returns list of available VLANs from the VLAN group `{{vlan_group}}`.

You can set a limit on the number of result records using the `limit` query parameter. For example, `/api/plugins/scripthelper/prefixes/{{prefix}}/available-ips/?limit=10` returns no more than 10 records.

Additionally `prefixes/{{prefix}}/available-prefixes/` provides a `prefixlen` query parameter, which specifies that the returned networks have fixed size.

### Example

```
import extras.scripts as es
from ipam.models import Prefix
from netbox_scripthelper.fields import DynamicChoiceVar


class ExampleDynamicChoiceField(es.Script):
    class Meta:
        name = "Dynamic Choice Field Exmaple"

    prefix = es.ObjectVar(
        model=Prefix,
    )
    # show available IP addresses from the prefix specified in the field above
    address = DynamicChoiceVar(
        api_url="/api/plugins/scripthelper/prefixes/{{prefix}}/available-ips/",
        label='Address',
    )
    
    # show available VLANs from the fixed VLAN group with ID 10
    vlan = DynamicChoiceVar(
        api_url="/api/plugins/scripthelper/vlan-groups/10/available-vlans/",
        label='VLAN',
    )
    
    # show no more than 20 child prefixes from the prefix {{prefix}} with size of 24
    child_prefix = DynamicChoiceVar(
        api_url="/api/plugins/scripthelper/prefixes/{{prefix}}/available-prefixes/",
        label='Child prefix',
        query_params={
            'limit': 20,
            'prefixlen': 24,
        }
    )

    def run(self, data, commit):
        # data['address'] => selected IP Address as string
        # data['vlan'] => selected VID as string
        # data['child_prefix'] => selected child prefix with mask as string
        pass

```

## ExpandableStringVar

A small wrapper around the NetBox original `ExpandableNameField` for use in custom scripts. The field allows for numeric range expansion, such as `Gi0/[1-3]`. 


### Example

```
import extras.scripts as es
from netbox_scripthelper.fields import ExpandableStringVar


class ExampleExpandableStringVar(es.Script):

    vm_name = ExpandableStringVar(
        label='Name',
        description="Alphanumeric ranges are supported for bulk creation. (example: my-new-vm[1-3].exmaple.com)."
    )

    def run(self, data, commit):
        # data['vm_name'] => ['my-new-vm1.exmaple.com', 'my-new-vm2.exmaple.com', 'my-new-vm3.exmaple.com']
        pass

```

## make_link

The helper returns a reference to the object enclosed in the `<a>` tag. This can be useful in a script output.

```
...
from netbox_scripthelper.utils import make_link as _ml


class ExampleMakeLink(Script):

...

    def run(self, data, commit):
        ...
        prefix = Prefix.objects.create(prefix='192.168.0.0/24')
        self.info_log(f'Created prefix: {_ml(prefix)}')

```

## IPSpliter

IPSliter splits set of networks to smaller networks with fixed mask.

```
from netbox_scripthelper.utils import IPSpliter
from netaddr import IPSet, IPNetwork

spliter = IPSplitter(IPSet([
    IPNetwork('192.168.1.0/24'),
    IPNetwork('192.168.3.0/24')
]))

# subnets => [IPNetwork('192.168.1.0/28', '192.168.1.16/28', ...)]
subnetes = spliter.split(28)
```

## process_event_queue

Inspired by https://github.com/netbox-community/netbox/issues/14896.

The `process_event_queue` helper allows you to pass a snapshot of object changes to a script call on an event.

### How to use

1. Override original events_pipeline in configuration.py:
```
EVENTS_PIPELINE = ('netbox_scripthelper.events.process_event_queue', )
```

2. Create a new event rule with the Script action type.
3. In the script handler, refer to the additional attributes:
```
    def run(self, data, commit):
        if 'snapshots' not in data:
            return
        postchange = data['snapshots']['postchange']
        prechange = data['snapshots']['prechange']
        event = data['event']
        username = data['username']

```

