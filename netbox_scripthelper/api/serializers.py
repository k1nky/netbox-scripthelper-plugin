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
        return {
            'id': f"{instance}/{self.context['parent'].mask_length}",
            'display': f"{instance}/{self.context['parent'].mask_length}",
        }
