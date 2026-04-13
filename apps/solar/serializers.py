from rest_framework import serializers

from .services import SolarResourceReading


class SolarResourceReadingSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    annual_avg_dni = serializers.FloatField(allow_null=True)
    annual_avg_ghi = serializers.FloatField(allow_null=True)
    annual_avg_lat_tilt = serializers.FloatField(allow_null=True)
    monthly_avg_dni = serializers.DictField(allow_null=True)
    monthly_avg_ghi = serializers.DictField(allow_null=True)
    monthly_avg_lat_tilt = serializers.DictField(allow_null=True)

    def create(self, validated_data):
        return SolarResourceReading(**validated_data)


class PVWattsCalculationSerializer(serializers.Serializer):
    site_id = serializers.IntegerField()
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    system_size_kw = serializers.FloatField(default=1)
    irradiance_kwh_m2_day = serializers.FloatField(default=4)
    estimated_daily_kwh = serializers.FloatField(read_only=True)

