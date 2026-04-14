from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from rest_framework import status

import logging
import requests

from config.config import GEOCODING_SERVICE_URL, APP_USER_AGENT


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class GeocodedLocation:
    address: str
    latitude: float | None
    longitude: float | None
    source: str = "nominatim"


def geocode_address(address: str) -> GeocodedLocation:
    """Geocode an address string using an external geocoding service."""
    
    logger.debug(f"Attempting to geocode address: '{address}' using {GEOCODING_SERVICE_URL}")

    api_url = f"{GEOCODING_SERVICE_URL}"
    
    payload = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        'User-Agent': APP_USER_AGENT
    }

    try:
        response = requests.get(api_url, headers=headers, params=payload)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Error occurred while geocoding address '{address}' due to: {e}")
        return None, status.HTTP_500_INTERNAL_SERVER_ERROR
        
    if data and isinstance(data, list) and len(data) > 0:
        location_data = data[0]
        logger.debug(f"Successfully geocoded address '{address}' to lat: {location_data['lat']}, lon: {location_data['lon']} using {GEOCODING_SERVICE_URL}")
        return GeocodedLocation(
            address=address,
            latitude=float(location_data["lat"]),
            longitude=float(location_data["lon"]),
            source=GEOCODING_SERVICE_URL.split("//")[-1].split("/")[0]  # Extract domain as source
        ), status.HTTP_200_OK
    else:
        logger.warning(f"No geocoding results found for address '{address}' using {GEOCODING_SERVICE_URL}")
        return None, status.HTTP_404_NOT_FOUND

