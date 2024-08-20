from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from ipam.models import VLAN, VLANGroup, Prefix, IPAddress, IPRange
from netbox.api.viewsets.mixins import ObjectValidationMixin

from .serializers import (AvailableVLANSerializer,
                          AvailablePrefixSerializer,
                          AvailableIPSerializer)
from netbox_scripthelper.utils import IPSplitter


def get_results_limit(request):
    try:
        return int(request.query_params.get('limit', None))
    except TypeError:
        return None


class AvailableIPAddressesView(ObjectValidationMixin, APIView):
    queryset = IPAddress.objects.all()

    def get_parent(self, request, pk):
        raise NotImplementedError

    def get(self, request, pk):
        parent = self.get_parent(request, pk)
        limit = get_results_limit(request)

        # Calculate available IPs within the parent
        ip_list = []
        for index, ip in enumerate(parent.get_available_ips(), start=1):
            if index == limit:
                break
            ip_list.append(ip)
        serializer = AvailableIPSerializer(ip_list, many=True, context={
            'request': request,
            'parent': parent,
            'vrf': parent.vrf,
        })
        return Response(
            {
                'results': serializer.data
            }
        )


class PrefixAvailableIPAddressesView(AvailableIPAddressesView):

    def get_parent(self, request, pk):
        return get_object_or_404(Prefix.objects.restrict(request.user), pk=pk)


class IPRangeAvailableIPAddressesView(AvailableIPAddressesView):

    def get_parent(self, request, pk):
        return get_object_or_404(IPRange.objects.restrict(request.user), pk=pk)


class AvailableVLANsView(ObjectValidationMixin, APIView):
    queryset = VLAN.objects.all()

    def get(self, request, pk):
        vlangroup = get_object_or_404(VLANGroup.objects.restrict(request.user), pk=pk)
        limit = get_results_limit(request)

        available_vlans = vlangroup.get_available_vids()[:limit]
        serializer = AvailableVLANSerializer(available_vlans, many=True, context={
            'request': request,
            'group': vlangroup,
        })
        return Response(
            {
                'results': serializer.data
            }
        )


class AvailablePrefixesView(ObjectValidationMixin, APIView):
    queryset = Prefix.objects.all()

    def get(self, request, pk):
        prefix = get_object_or_404(Prefix.objects.restrict(request.user), pk=pk)
        available_prefixes = prefix.get_available_prefixes()
        prefix_len = int(request.query_params.get('prefixlen', 0))
        limit = get_results_limit(request)
        subnets = IPSplitter(available_prefixes).split(prefix_len, limit)

        serializer = AvailablePrefixSerializer(subnets, many=True, context={
            'request': request,
            'vrf': prefix.vrf,
        })
        return Response(
            {
                'results': serializer.data
            }
        )
