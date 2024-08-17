from django.urls import path

from . import views

app_name = 'scripthelper'

urlpatterns = [
    # TODO: urls:ip-ranges
    # path(
    #     'ip-ranges/<int:pk>/available-ips/',
    #     views.IPRangeAvailableIPAddressesView.as_view(),
    #     name='iprange-available-ips'
    # ),
    path(
        'prefixes/<int:pk>/available-prefixes/',
        views.AvailablePrefixesView.as_view(),
        name='prefix-available-prefixes'
    ),
    path(
        'prefixes/<int:pk>/available-ips/',
        views.PrefixAvailableIPAddressesView.as_view(),
        name='prefix-available-ips'
    ),
    path(
        'vlan-groups/<int:pk>/available-vlans/',
        views.AvailableVLANsView.as_view(),
        name='vlangroup-available-vlans'
    ),
]
