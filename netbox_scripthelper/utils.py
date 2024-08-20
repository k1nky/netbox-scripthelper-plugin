from typing import List
from netaddr import IPSet, IPNetwork, IPAddress
from django.core.exceptions import ValidationError
from ipam.models import Prefix


class IPSplitter:
    """
    Split prefixes into subnets with fixed prefix length.
    """

    def __init__(self, prefixes: IPSet):
        self.prefixes = prefixes

    def split(self, prefix_len: int, limit: int) -> List[IPNetwork]:
        subnets = []
        if prefix_len == 0:
            return list(self.prefixes.iter_cidrs())
        for free_net in self.prefixes.iter_cidrs():
            if free_net.prefixlen > prefix_len:
                continue
            subnets.extend(list(free_net.subnet(prefix_len)))
            if limit and len(subnets) > limit:
                subnets = subnets[:limit]
                break

        return subnets


def get_available_ip_list(prefix: Prefix, base_addr: str, size: int) -> List[IPAddress]:
    available_addresses = prefix.get_available_ips()
    base_addr = base_addr.split('/')[0]
    addresses = []
    for i in range(0, size):
        next_addr = IPAddress(base_addr) + i
        if next_addr in available_addresses:
            addresses.append(next_addr)
    if len(addresses) != size:
        raise ValidationError("not enough free addresses")
    return addresses
