# NetBox Scripthelper

Collections of utilities for Netbox custom scripts.

# Helpers

## DynamicChoiceField

Inspired by https://github.com/netbox-community/netbox/discussions/9326.
This field allows you to select available models (such as VLAN, Prefix, Address) in the NetBox Script interface.

```
import extras.scripts as es
from ipam.models import Prefix
from netbox_scripthelper.fields import DynamicChoiceVar


class ExampleDynamicChoiceField(es.Script):
    class Meta:
        name = "Dynamic Choice Field Exmaple"

    prefix = es.ObjectVar(
        model=Prefix,
        required=True,
    )
    address = DynamicChoiceVar(
        api_url="/api/plugins/scripthelper/prefixes/{{prefix}}/available-ips/",
        label='Address',
        required=True,
    )

```