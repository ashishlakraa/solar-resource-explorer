from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .serializers import PVWattsCalculationSerializer, SolarSiteSerializer
from .services import calculate_pvwatts, fetch_irradiance


class SolarSiteViewSet(ViewSet):
    """ViewSet for solar site operations."""

    @action(detail=True, methods=["get"], url_path="detail")
    def site_detail(self, request, pk=None):
        """Get solar site details."""
        return Response(
            SolarSiteSerializer(
                {"site_id": pk, "detail": "Solar site detail endpoint stub."}
            ).data
        )

    @action(detail=True, methods=["get"], url_path="pvwatts")
    def pvwatts(self, request, pk=None):
        """Calculate PVWatts production estimate for a solar site."""
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        system_size_kw = float(request.query_params.get("system_size_kw", 1))
        irradiance_kwh_m2_day = float(
            request.query_params.get("irradiance_kwh_m2_day", 4)
        )

        if latitude is not None and longitude is not None:
            fetch_irradiance(float(latitude), float(longitude))

        try:
            estimated_daily_kwh = calculate_pvwatts(
                system_size_kw, irradiance_kwh_m2_day
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        result = {
            "site_id": pk,
            "system_size_kw": system_size_kw,
            "irradiance_kwh_m2_day": irradiance_kwh_m2_day,
            "estimated_daily_kwh": estimated_daily_kwh,
        }
        return Response(PVWattsCalculationSerializer(result).data)
