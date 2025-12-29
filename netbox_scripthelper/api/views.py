from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from ipam.models import VLAN, VLANGroup, Prefix, IPAddress, IPRange
from netbox.api.viewsets.mixins import ObjectValidationMixin

from .serializers import (AvailableVLANSerializer,
                          AvailablePrefixSerializer,
                          AvailableIPSerializer,
                          ChildIPSerializer)
from netbox_scripthelper.utils import IPSplitter


def get_results_limit(request):
    try:
        return int(request.query_params.get('limit', None))
    except TypeError:
        return None


def filter_results(request, objects):
    q = request.query_params.get('q', '')
    limit = get_results_limit(request)
    filtered = []
    for x in objects:
        if limit and len(filtered) > limit:
            break
        if q and not str(x).startswith(str(q)):
            continue
        filtered.append(x)

    return filtered[:limit]


class AvailableIPAddressesView(ObjectValidationMixin, APIView):
    queryset = IPAddress.objects.all()

    def get_parent(self, request, pk):
        raise NotImplementedError

    def get(self, request, pk):
        parent = self.get_parent(request, pk)

        # Calculate available IPs within the parent
        ip_list = filter_results(request, parent.get_available_ips())
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

        available_vlans = filter_results(request, vlangroup.get_available_vids())
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
        subnets = IPSplitter(available_prefixes).split(prefix_len)
        subnets = filter_results(request, subnets)

        serializer = AvailablePrefixSerializer(subnets, many=True, context={
            'request': request,
            'vrf': prefix.vrf,
        })
        return Response(
            {
                'results': serializer.data
            }
        )


class PrefixChildIPAddressesView(ObjectValidationMixin, APIView):
    queryset = IPAddress.objects.all()

    def get_parent(self, request, pk):
        return get_object_or_404(Prefix.objects.restrict(request.user), pk=pk)

    def get(self, request, pk):
        parent = self.get_parent(request, pk)

        ip_list = filter_results(request, parent.get_child_ips())
        serializer = ChildIPSerializer(ip_list, many=True, context={
            'request': request,
            'parent': parent,
            'vrf': parent.vrf,
        })
        return Response(
            {
                'results': serializer.data
            }
        )
