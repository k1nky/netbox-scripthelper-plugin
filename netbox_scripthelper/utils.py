from typing import List, Any
from netaddr import IPSet, IPNetwork, IPAddress, IPRange


class IPSplitter:
    """
    Split prefixes into subnets with fixed prefix length.
    """

    def __init__(self, prefixes: IPSet):
        self.prefixes = prefixes

    def split(self, prefix_len: int, limit: int = None) -> List[IPNetwork]:
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


def get_available_ips_list(ipset: IPSet, base_addr: str, size: int) -> List[IPAddress]:
    """
    Returns a list of addresses from `ipset`, starting with `base_addr`.
    The size of the list is limited by the "size" argument.
    Raises IndexError if there are not enough free addresses.
    """

    base_addr = base_addr.split('/')[0]
    all = IPSet(['0.0.0.0/0'])
    excluded = IPSet([IPRange('0.0.0.0', IPAddress(base_addr) - 1),])

    availables = (all ^ excluded) & ipset
    addresses = []
    for ip in availables:
        if len(addresses) >= size:
            break
        addresses.append(ip)
    if len(addresses) != size:
        raise IndexError("not enough free addresses")
    return addresses


def make_link(obj: Any) -> str:
    """
    Returns a reference to the object enclosed in the <a> tag.
    """

    try:
        return f'<a href="{obj.get_absolute_url()}">{str(obj)}</a>'
    except Exception:
        return str(obj)
