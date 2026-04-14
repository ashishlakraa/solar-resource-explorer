from rest_framework import serializers

from .services import GeocodedLocation


class GeocodedLocationSerializer(serializers.Serializer):
    address = serializers.CharField()
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)
    source = serializers.CharField()

    def create(self, validated_data):
        return GeocodedLocation(**validated_data)
