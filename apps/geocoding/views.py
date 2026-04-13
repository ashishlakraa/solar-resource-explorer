from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .serializers import GeocodedLocationSerializer
from .services import geocode_payload

import requests

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

        address = request.query_params.get("address", "").strip()
        
        if not address:
            return Response(
                {
                    "detail": "Query parameter 'address' is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = geocode_payload(address)
        serializer = GeocodedLocationSerializer(result)
        return Response(serializer.data)
