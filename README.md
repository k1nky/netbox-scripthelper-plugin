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