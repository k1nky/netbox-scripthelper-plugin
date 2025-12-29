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
        with_mask = self.context['request'].query_params.get('with_mask', 'true').lower()

        value = str(instance)
        if with_mask == 'true':
            value = f"{instance}/{self.context['parent'].mask_length}"

        return {
            'id': value,
            'display': value,
        }

class ChildIPSerializer(serializers.Serializer):
    """
    Representation of an IP address which exists in the database.
    """
    def to_representation(self, instance):

        value = str(instance)

        return {
            'id': value,
            'display': value,
        }
