from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .serializers import GeocodedLocationSerializer
from .services import geocode_payload

import requests

class GeocodingViewSet(ViewSet):
    """ViewSet for geocoding operations."""

    @action(detail=False, methods=["get"], url_path="geocode")
    def geocode(self, request):
        """Geocode an address string."""
        address = request.query_params.get("address", "").strip()
        
        if not address:
            return Response(
                {"detail": "Query parameter 'address' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = geocode_payload(address)
        serializer = GeocodedLocationSerializer(result)
        return Response(serializer.data)
