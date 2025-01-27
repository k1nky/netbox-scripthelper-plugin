try:
    from netbox.plugins import PluginConfig
except ModuleNotFoundError:
    # NetBox <= 3.4
    from extras.plugins import PluginConfig


class ScriptHelperConfig(PluginConfig):
    name = 'netbox_scripthelper'
    verbose_name = 'NetBox ScriptHelper'
    description = 'Collections of utilities for Netbox custom scripts.'
    version = '0.3.2'
    author = 'Andrey Shalashov'
    author_email = 'avshalashov@yandex.ru'
    base_url = 'scripthelper'
    required_settings = []
    default_settings = {}
    django_apps = []
    min_version = '3.3.0'
    max_version = '4.2.99'


config = ScriptHelperConfig
