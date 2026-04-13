import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .serializers import GeocodedLocationSerializer
from .services import geocode_address


logger = logging.getLogger(__name__)

class GeocodingViewSet(ViewSet):
    """ViewSet for geocoding operations."""
    
    serializer_class = GeocodedLocationSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="address",
                location=OpenApiParameter.QUERY,
                description="The address to geocode",
                required=True,
                type=OpenApiTypes.STR,
            )
        ],
        responses={200: GeocodedLocationSerializer}
    )
    @action(detail=False, methods=["get"], url_path="search")
    def geocode(self, request):
        """Geocode given address string."""

        logger.info(f"Received geocoding request with query params: {request.query_params}")

        address = request.query_params.get("address", "").strip()
        logger.debug(f"Attempting to geocode address: {address}")
        if not address:
            return Response(
                {
                    "detail": "Query parameter 'address' is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result, status_code = geocode_address(address)

        if status_code != status.HTTP_200_OK:

            if status_code == status.HTTP_404_NOT_FOUND:
                return Response(
                    {
                        "detail": f"Address '{address}' not found"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                return Response(
                    {
                        "detail": f"Some error occurred while geocoding address '{address}'"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            serializer = GeocodedLocationSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
