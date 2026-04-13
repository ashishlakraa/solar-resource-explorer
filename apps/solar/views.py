from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .serializers import PVWattsCalculationSerializer, SolarSiteSerializer
from .services import calculate_pvwatts, fetch_irradiance


class SolarSiteViewSet(ViewSet):
    """ViewSet for solar site operations."""
    
    serializer_class = SolarSiteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="latitude",
                location=OpenApiParameter.HEADER,
                description="The latitude coordinate of the solar site",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="longitude",
                location=OpenApiParameter.HEADER,
                description="The longitude coordinate of the solar site",
                required=True,
                type=OpenApiTypes.FLOAT,
            )
        ],
        responses={200: SolarSiteSerializer}
    )
    @action(detail=False, methods=["get"], url_path="detail")
    def site_detail(self, request):
        """Get solar resource details."""
        



        return Response(
            SolarSiteSerializer(
                {"site_id": pk, "detail": "Solar site detail endpoint stub."}
            ).data
        )

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             name="id",
    #             location=OpenApiParameter.PATH,
    #             description="The ID of the solar site",
    #             required=True,
    #             type=OpenApiTypes.INT,
    #         ),
    #         OpenApiParameter(
    #             name="latitude",
    #             location=OpenApiParameter.QUERY,
    #             description="Latitude of the solar site",
    #             required=False,
    #             type=OpenApiTypes.FLOAT,
    #         ),
    #         OpenApiParameter(
    #             name="longitude",
    #             location=OpenApiParameter.QUERY,
    #             description="Longitude of the solar site",
    #             required=False,
    #             type=OpenApiTypes.FLOAT,
    #         ),
    #         OpenApiParameter(
    #             name="system_size_kw",
    #             location=OpenApiParameter.QUERY,
    #             description="System size in kilowatts",
    #             required=False,
    #             type=OpenApiTypes.FLOAT,
    #         ),
    #         OpenApiParameter(
    #             name="irradiance_kwh_m2_day",
    #             location=OpenApiParameter.QUERY,
    #             description="Irradiance in kWh/m2/day",
    #             required=False,
    #             type=OpenApiTypes.FLOAT,
    #         ),
    #     ],
    #     responses={200: PVWattsCalculationSerializer}
    # )
    # @action(detail=True, methods=["get"], url_path="pvwatts")
    # def pvwatts(self, request, pk: int = None):
    #     """Calculate PVWatts production estimate for a solar site."""
    #     latitude = request.query_params.get("latitude")
    #     longitude = request.query_params.get("longitude")
    #     system_size_kw = float(request.query_params.get("system_size_kw", 1))
    #     irradiance_kwh_m2_day = float(
    #         request.query_params.get("irradiance_kwh_m2_day", 4)
    #     )

    #     if latitude is not None and longitude is not None:
    #         fetch_irradiance(float(latitude), float(longitude))

    #     try:
    #         estimated_daily_kwh = calculate_pvwatts(
    #             system_size_kw, irradiance_kwh_m2_day
    #         )
    #     except ValueError as e:
    #         return Response(
    #             {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
    #         )

    #     result = {
    #         "site_id": pk,
    #         "system_size_kw": system_size_kw,
    #         "irradiance_kwh_m2_day": irradiance_kwh_m2_day,
    #         "estimated_daily_kwh": estimated_daily_kwh,
    #     }
    #     return Response(PVWattsCalculationSerializer(result).data)
