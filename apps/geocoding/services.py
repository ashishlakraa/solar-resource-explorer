from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

@dataclass(frozen=True)
class GeocodedLocation:
    address: str
    latitude: float | None
    longitude: float | None
    source: str = "nominatim"


def geocode_address(address: str) -> GeocodedLocation:
    """Placeholder geocoding hook for future Nominatim integration."""

    url = "https://nominatim.openstreetmap.org/search?q=College Avenue Student Center, New Brunswick&format=json&limit=1"

    payload = {}
    headers = {
        'User-Agent': 'solar-resource-explorer'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)



    return GeocodedLocation(address=address, latitude=None, longitude=None)


def geocode_payload(address: str) -> dict[str, Any]:
    location = geocode_address(address)
    return {
        "address": location.address,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "source": location.source,
    }
