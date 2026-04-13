from __future__ import annotations

from dataclasses import dataclass
import logging
import requests
from rest_framework import status

from config.config import NREL_SOLAR_RESOURCE_URL, NREL_API_KEY

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class SolarResourceReading:
    latitude: float
    longitude: float
    annual_ghi_kwh_m2: float | None = None
    annual_dni_kwh_m2: float | None = None
    annual_dhi_kwh_m2: float | None = None


def fetch_irradiance(latitude: float, longitude: float) -> SolarResourceReading:
    """Placeholder solar resource lookup for future NREL integration."""

    api_url = f"{NREL_SOLAR_RESOURCE_URL}"

    payload = {
        "lat": latitude,
        "lon": longitude,
        "api_key": f"{NREL_API_KEY}",
        "format": "json"
    }

    try:
        response = requests.get(api_url, params=payload)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Error occurred while fetching solar resource data for lat: {latitude}, lon: {longitude} due to: {e}")
        return None, status.HTTP_500_INTERNAL_SERVER_ERROR




def calculate_pvwatts(
    system_size_kw: float,
    irradiance_kwh_m2_day: float,
    performance_ratio: float = 0.8,
) -> float:
    """Simple PVWatts-style production estimate in kWh per day."""
    if system_size_kw < 0:
        raise ValueError("system_size_kw must be non-negative")
    if irradiance_kwh_m2_day < 0:
        raise ValueError("irradiance_kwh_m2_day must be non-negative")
    if not 0 < performance_ratio <= 1:
        raise ValueError("performance_ratio must be between 0 and 1")

    return system_size_kw * irradiance_kwh_m2_day * performance_ratio
