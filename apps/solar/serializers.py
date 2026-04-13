from rest_framework import serializers

from .services import SolarResourceReading


class SolarResourceReadingSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    annual_ghi_kwh_m2 = serializers.FloatField(allow_null=True)
    annual_dni_kwh_m2 = serializers.FloatField(allow_null=True)
    annual_dhi_kwh_m2 = serializers.FloatField(allow_null=True)

    def create(self, validated_data):
        return SolarResourceReading(**validated_data)


class PVWattsCalculationSerializer(serializers.Serializer):
    site_id = serializers.IntegerField()
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    system_size_kw = serializers.FloatField(default=1)
    irradiance_kwh_m2_day = serializers.FloatField(default=4)
    estimated_daily_kwh = serializers.FloatField(read_only=True)


class SolarSiteSerializer(serializers.Serializer):
    site_latitude = serializers.FloatField()
    site_longitude = serializers.FloatField()
