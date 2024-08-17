from typing import List
from netaddr import IPSet, IPNetwork


class IPSplitter:
    """
    Split prefixes into subnets with fixed prefix length.
    """

    def __init__(self, prefixes: IPSet):
        self.prefixes = prefixes

    def split(self, prefix_len: int) -> List[IPNetwork]:
        subnets = []
        if prefix_len == 0:
            return list(self.prefixes.iter_cidrs())
        for free_net in self.prefixes.iter_cidrs():
            if free_net.prefixlen > prefix_len:
                continue
            subnets.extend(list(free_net.subnet(prefix_len)))

        return subnets
