import unittest
from netaddr import IPSet, IPNetwork, IPAddress, IPRange
from netbox_scripthelper.utils import get_available_ips_list, IPSplitter


class TestGetAvailableIPList(unittest.TestCase):

    def test_full_network(self):
        ipset = IPSet([IPNetwork('192.168.1.0/24'),])
        iplist = get_available_ips_list(ipset, '192.168.1.10', 3)
        self.assertListEqual(iplist, [IPAddress('192.168.1.10'), IPAddress('192.168.1.11'), IPAddress('192.168.1.12')])

    def test_range_with_hole(self):
        ipset = IPSet([IPRange('192.168.1.1', '192.168.1.11'), IPRange('192.168.1.13', '192.168.1.20')])
        iplist = get_available_ips_list(ipset, '192.168.1.10', 3)
        self.assertListEqual(iplist, [IPAddress('192.168.1.10'), IPAddress('192.168.1.11'), IPAddress('192.168.1.13')])

    def test_not_enough(self):
        ipset = IPSet([IPRange('192.168.1.10', '192.168.1.11'), IPRange('192.168.1.13', '192.168.1.20')])
        raised = False
        try:
            get_available_ips_list(ipset, '192.168.1.10', 30)
        except IndexError:
            raised = True
        self.assertTrue(raised)


class TestIPSplitter(unittest.TestCase):

    def test(self):
        cases = [
            ("limit", IPSet([IPNetwork('192.168.1.0/24'),]), (30, 2), [IPNetwork('192.168.1.0/30'), IPNetwork('192.168.1.4/30')]),
            ("no limit", IPSet([IPNetwork('192.168.1.0/29'),]), (30,), [IPNetwork('192.168.1.0/30'), IPNetwork('192.168.1.4/30')]),
            ("no free space", IPSet([IPNetwork('192.168.1.0/29'),]), (28,), [])
        ]
        for case in cases:
            got = IPSplitter(case[1]).split(*case[2])
            self.assertListEqual(case[-1], got, case[0])
        IPSplitter(IPSet([IPNetwork("10.0.0.0/16"),])).split(24)
