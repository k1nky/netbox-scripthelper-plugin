from rest_framework import serializers


class AvailableVLANSerializer(serializers.Serializer):
    """
    Representation of a VLAN which does not exist in the database.
    """

    def to_representation(self, instance):
        return {
            'id': instance,
            'display': instance,
        }


class AvailablePrefixSerializer(serializers.Serializer):
    """
    Representation of a prefix which does not exist in the database.
    """

    def to_representation(self, instance):
        return {
            'id': str(instance),
            'display': str(instance),
        }


class AvailableIPSerializer(serializers.Serializer):
    """
    Representation of an IP address which does not exist in the database.
    """
    def to_representation(self, instance):
        with_mask = self.context['request'].query_params.get('with_mask', 'True')

        value = f"{instance}/{self.context['parent'].mask_length}"
        if with_mask == 'False':
            value = str(instance)

        return {
            'id': value,
            'display': value,
        }
