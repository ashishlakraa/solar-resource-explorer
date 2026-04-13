import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .serializers import PVWattsCalculationSerializer, SolarResourceReadingSerializer
from .services import fetch_solar_resource_data


logger = logging.getLogger(__name__)

class SolarSiteViewSet(ViewSet):
    """ViewSet for solar site operations."""
    
    serializer_class = SolarResourceReadingSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="latitude",
                location=OpenApiParameter.QUERY,
                description="The latitude coordinate of the solar site",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="longitude",
                location=OpenApiParameter.QUERY,
                description="The longitude coordinate of the solar site",
                required=True,
                type=OpenApiTypes.FLOAT,
            )
        ],
        responses={200: SolarResourceReadingSerializer}
    )
    @action(detail=False, methods=["get"], url_path="detail")
    def site_detail(self, request):
        """Get solar resource details."""
        
        logger.info(f"Received solar site detail request with query params: {request.query_params}")

        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")

        if latitude is None or longitude is None:
            return Response(
                {
                    "detail": "Query parameters 'latitude' and 'longitude' are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        result, status_code = fetch_solar_resource_data(float(latitude), float(longitude))

        if status_code != status.HTTP_200_OK:
            return Response(
                {
                    "detail": f"Error fetching solar resource data for lat: {latitude}, lon: {longitude}"
                },
                status=status_code,
            )
        else:
            serializer = SolarResourceReadingSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="lat",
                location=OpenApiParameter.QUERY,
                description="The latitude for the location to use (Range: -90 to 90)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="lon",
                location=OpenApiParameter.QUERY,
                description="The longitude for the location to use (Range: -180 to 180)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="system_capacity",
                location=OpenApiParameter.QUERY,
                description="Nameplate capacity in kilowatts (Range: 0.05 to 500000)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="module_type",
                location=OpenApiParameter.QUERY,
                description="""Module type (Options: 0, 1, 2)
                0 = Standard
                1 = Premium
                2 = Thin film""",
                required=True,
                type=OpenApiTypes.INT,
                enum=[0, 1, 2]
            ),
            OpenApiParameter(
                name="losses",
                location=OpenApiParameter.QUERY,
                description="System losses in percent (Range: -5 to 99)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="array_type",
                location=OpenApiParameter.QUERY,
                description="""Array type (Options: 0, 1, 2, 3, 4)
                0 = Fixed - Open Rack
                1 = Fixed - Roof Mounted
                2 = Fixed - 1-Axis
                3 = Fixed - 1-Axis Backtracking
                4 = Fixed - 2-Axis""",
                required=True,
                type=OpenApiTypes.INT,
                enum=[0, 1, 2, 3, 4]
            ),
            OpenApiParameter(
                name="tilt",
                location=OpenApiParameter.QUERY,
                description="Tilt angle in degrees (Range: 0 to 90)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="azimuth",
                location=OpenApiParameter.QUERY,
                description="Azimuth angle in degrees (Range: 0 to 360)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="dc_ac_ratio",
                location=OpenApiParameter.QUERY,
                description="DC to AC ratio (default: 1.2)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="inv_eff",
                location=OpenApiParameter.QUERY,
                description="Inverter efficiency at rated power (Range: 90 - 99.5, default: 96)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="gcr",
                location=OpenApiParameter.QUERY,
                description="Ground coverage ratio (Range: 0.01 - 0.99, default: 0.4)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="albedo",
                location=OpenApiParameter.QUERY,
                description="Ground reflectance (Range: 0 - 1)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="bifaciality",
                location=OpenApiParameter.QUERY,
                description="Ratio of rear-side efficiency to front-side efficiency (Range: 0 - 1)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="soiling",
                location=OpenApiParameter.QUERY,
                description="Monthly soiling losses as pipe-delimited array (12 values, Range: 0 - 100)",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: PVWattsCalculationSerializer}
    )
    @action(detail=True, methods=["get"], url_path="pvwatts")
    def pvwatts(self, request, pk: int = None):
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
