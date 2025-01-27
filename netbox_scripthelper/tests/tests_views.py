import unittest
import unittest.mock as mock
from utilities.testing.base import TestCase

from django.urls import reverse
from django.test import override_settings
from rest_framework import status

from ipam.models import VLANGroup, VLAN, Prefix, IPAddress
from netbox_scripthelper.api.views import filter_results
from django.db.backends.postgresql.psycopg_any import NumericRange


class TestFilterResults(unittest.TestCase):

    def create_request(self, **kwargs):
        mm = mock.MagicMock()
        mm.query_params = kwargs
        return mm

    def test(self):

        cases = [
            ("empty", self.create_request(), [], []),
            ("only limit", self.create_request(limit=2), [1, 2, 3, 4, 5], [1, 2]),
            ("only limit: all", self.create_request(limit=20), [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ("only q: matched", self.create_request(q=2), [1, 2, 3, 20, 5], [2, 20]),
            ("only q: not matched", self.create_request(q=7), [1, 2, 3, 20, 5], []),
            ("q and limit", self.create_request(q=2, limit=2), [1, 2, 3, 20, 21], [2, 20]),
            ("q and limit: all", self.create_request(q=2, limit=10), [1, 2, 3, 20, 21], [2, 20, 21]),
        ]

        for case in cases:
            got = filter_results(case[1], case[2])
            self.assertListEqual(got, case[-1], case[0])


class TestAvailablesVLANS(TestCase):

    @classmethod
    def setUpTestData(cls):
        VLANGroup.objects.create(name='TestVG1', slug='testvg1', vid_ranges=[NumericRange(100, 1000, bounds='[]')])
        vg2 = VLANGroup.objects.create(name='TestVG2', slug='testvg2', vid_ranges=[NumericRange(10, 15, bounds='[]')])
        VLAN.objects.create(name='TestVlan2', vid=12, group=vg2)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], LOGIN_REQUIRED=False)
    def test(self):
        cases = [
            ("no_limit_no_filter", "", 5),
            ("with_limit_no_filter", "?limit=10", 5),
            ("with_limit_with_filter_not_match", "?limit=10&q=2", 0),
            ("with_limit_with_filter_match", "?limit=2&q=1", 2),
            ("no_limit_with_filter", "?q=1", 5),
        ]
        vg = VLANGroup.objects.get(name='TestVG2')
        url = reverse('plugins-api:netbox_scripthelper-api:vlangroup-available-vlans', kwargs={'pk': vg.pk})
        for case in cases:
            response = self.client.get(f'{url}{case[1]}')
            self.assertEqual(response.status_code, status.HTTP_200_OK, case[0])
            self.assertEqual(len(response.data['results']), case[-1], case[0])


class TestAvailablesPrefixes(TestCase):

    @classmethod
    def setUpTestData(cls):
        Prefix.objects.create(prefix='172.20.0.0/24')
        Prefix.objects.create(prefix='172.20.0.128/27')
        Prefix.objects.create(prefix='172.20.0.192/27')

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], LOGIN_REQUIRED=False)
    def test_fixed_mask(self):
        cases = [
            ("no_limit_no_filter", "?prefixlen=27", 6),
            ("with_limit_no_filter", "?prefixlen=27&limit=3", 3),
            ("with_limit_with_filter", "?prefixlen=27&limit=3&q=172.20.0.1", 1),
            ("no_limit_with_filter", "?prefixlen=27&q=172.20.0.1", 1),
        ]
        p = Prefix.objects.get(prefix='172.20.0.0/24')
        url = reverse('plugins-api:netbox_scripthelper-api:prefix-available-prefixes', kwargs={'pk': p.pk})
        for case in cases:
            response = self.client.get(f'{url}{case[1]}')
            self.assertEqual(response.status_code, status.HTTP_200_OK, case[0])
            self.assertEqual(len(response.data['results']), case[-1], case[0])

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], LOGIN_REQUIRED=False)
    def test(self):
        cases = [
            ("no_limit_no_filter", "", 3),
            ("with_limit_no_filter", "?limit=2", 2),
            ("with_limit_with_filter", "?limit=3&q=172.20.0.1", 1),
            ("empty", "?limit=3&q=172.30.0.1", 0),
        ]
        p = Prefix.objects.get(prefix='172.20.0.0/24')
        url = reverse('plugins-api:netbox_scripthelper-api:prefix-available-prefixes', kwargs={'pk': p.pk})
        for case in cases:
            response = self.client.get(f'{url}{case[1]}')
            self.assertEqual(response.status_code, status.HTTP_200_OK, case[0])
            self.assertEqual(len(response.data['results']), case[-1], case[0])


class TestAvailablesIPAddresses(TestCase):

    @classmethod
    def setUpTestData(cls):
        Prefix.objects.create(prefix='192.168.0.0/28')
        IPAddress.objects.bulk_create([
            IPAddress(address='192.168.0.2/28'),
            IPAddress(address='192.168.0.5/28')
        ])

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], LOGIN_REQUIRED=False)
    def test(self):
        cases = [
            ("no_limit_no_filter", "", 12),
            ("with_limit_no_filter", "?limit=5", 5),
            ("with_limit_with_filter", "?limit=3&q=192.168.0.1", 3),
            ("empty", "?limit=3&q=172.30.0.1", 0),
        ]
        p = Prefix.objects.get(prefix='192.168.0.0/28')
        url = reverse('plugins-api:netbox_scripthelper-api:prefix-available-ips', kwargs={'pk': p.pk})
        for case in cases:
            response = self.client.get(f'{url}{case[1]}')
            self.assertEqual(response.status_code, status.HTTP_200_OK, case[0])
            self.assertEqual(len(response.data['results']), case[-1], case[0])
