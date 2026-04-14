from __future__ import annotations

from dataclasses import dataclass
import logging
import requests
from rest_framework import status

from config.config import NREL_SOLAR_RESOURCE_URL, NREL_API_KEY, NREL_PVWATTS_URL

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class PVWattsCalculation:
    # Input parameters
    latitude: float
    longitude: float
    system_capacity: float
    module_type: int
    losses: float
    array_type: int
    tilt: float
    azimuth: float
    
    # Optional input parameters
    file_id: str = None
    dataset: str = None
    radius: int = None
    timeframe: str = None
    dc_ac_ratio: float = None
    gcr: float = None
    inv_eff: float = None
    bifaciality: float = None
    albedo: float = None
    soiling: list[float] | None = None
    
    # Output Station Info Fields
    station_lat: float = None
    station_lon: float = None
    elevation: float = None
    timezone: float = None
    location: str = None
    city: str = None
    state: str = None
    solar_resource_file: str = None
    distance: int = None
    weather_data_source: str = None
    
    # Output Fields
    ac_annual: float = None
    solrad_annual: float = None
    capacity_factor: float = None
    ac_monthly: list = None
    solrad_monthly: list = None
    poa_monthly: list = None
    dc_monthly: list = None


@dataclass(frozen=True)
class SolarResourceReading:
    # Input parameters
    latitude: float
    longitude: float
    
    # Output Annual data
    annual_avg_dni: float
    annual_avg_ghi: float
    annual_avg_lat_tilt: float
    
    # Output Monthly data
    monthly_avg_dni: dict
    monthly_avg_ghi: dict
    monthly_avg_lat_tilt: dict



def fetch_solar_resource_data(latitude: float, longitude: float) -> SolarResourceReading:
    """Fetch solar resource data from external NREL API and return SolarResourceReading."""

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
    
    # Check for API errors
    errors = data.get("errors", [])
    if errors:
        logger.error(f"API error occurred for lat: {latitude}, lon: {longitude} due to: {errors}")
        return None, response.status_code

    # Extract lat and lon
    inputs = data.get("inputs", {})
    lat = float(inputs.get("lat", latitude))
    lon = float(inputs.get("lon", longitude))
    
    # Extract outputs
    outputs = data.get("outputs", {})
    
    # Extract annual and monthly data for each metric
    avg_dni = outputs.get("avg_dni", {})
    if avg_dni == "no data":
        logger.warning(f"No DNI data available for lat: {latitude}, lon: {longitude} from NREL API")
        annual_avg_dni, monthly_avg_dni = None, None
    else:
        annual_avg_dni = avg_dni.get("annual", 0)
        monthly_avg_dni = avg_dni.get("monthly", {})
    
    avg_ghi = outputs.get("avg_ghi", {})
    if avg_ghi == "no data":
        logger.warning(f"No GHI data available for lat: {latitude}, lon: {longitude} from NREL API")
        annual_avg_ghi, monthly_avg_ghi = None, None
    else:
        annual_avg_ghi = avg_ghi.get("annual", 0)
        monthly_avg_ghi = avg_ghi.get("monthly", {})
    
    avg_lat_tilt = outputs.get("avg_lat_tilt", {})
    if avg_lat_tilt == "no data":
        logger.warning(f"No latitude tilt data available for lat: {latitude}, lon: {longitude} from NREL API")
        annual_avg_lat_tilt, monthly_avg_lat_tilt = None, None
    else:
        annual_avg_lat_tilt = avg_lat_tilt.get("annual", 0.0)
        monthly_avg_lat_tilt = avg_lat_tilt.get("monthly", {})
    
    # Create and return SolarResourceReading
    logger.debug(f"Successfully fetched solar resource data for lat: {latitude}, lon: {longitude} from NREL API with annual_avg_dni: {annual_avg_dni}, annual_avg_ghi: {annual_avg_ghi}, annual_avg_lat_tilt: {annual_avg_lat_tilt}")
    return SolarResourceReading(
        latitude=lat,
        longitude=lon,
        annual_avg_dni=annual_avg_dni,
        annual_avg_ghi=annual_avg_ghi,
        annual_avg_lat_tilt=annual_avg_lat_tilt,
        monthly_avg_dni=monthly_avg_dni,
        monthly_avg_ghi=monthly_avg_ghi,
        monthly_avg_lat_tilt=monthly_avg_lat_tilt
    ), status.HTTP_200_OK



def fetch_pvwatts_calculation(
    lat: float,
    lon: float,
    system_capacity: float,
    module_type: int,
    losses: float,
    array_type: int,
    tilt: float,
    azimuth: float,
    file_id: str = None,
    dataset: str = None,
    radius: int = None,
    timeframe: str = None,
    dc_ac_ratio: float = None,
    gcr: float = None,
    inv_eff: float = None,
    bifaciality: float = None,
    albedo: float = None,
    soiling: list[float] | None = None,
) -> tuple:
    """Fetch PVWatts calculation from NREL API and return PVWattsCalculation."""

    api_url = f"{NREL_PVWATTS_URL}"

    # Build payload with required parameters
    payload = {
        "lat": lat,
        "lon": lon,
        "system_capacity": system_capacity,
        "module_type": module_type,
        "losses": losses,
        "array_type": array_type,
        "tilt": tilt,
        "azimuth": azimuth,
        "api_key": f"{NREL_API_KEY}",
        "format": "json"
    }

    # Add optional parameters if provided
    if dc_ac_ratio is not None:
        payload["dc_ac_ratio"] = dc_ac_ratio
    if gcr is not None:
        payload["gcr"] = gcr
    if inv_eff is not None:
        payload["inv_eff"] = inv_eff
    if bifaciality is not None:
        payload["bifaciality"] = bifaciality
    if albedo is not None:
        payload["albedo"] = albedo
    if soiling is not None:
        # Pass list of floats directly to NREL API
        payload["soiling"] = soiling

    try:
        response = requests.get(api_url, params=payload)
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        logger.error(
            f"Error occurred while fetching PVWatts calculation for lat: {lat}, lon: {lon}, "
            f"system_capacity: {system_capacity} due to: {e}"
        )
        return None, status.HTTP_500_INTERNAL_SERVER_ERROR

    # Check for API errors
    errors = data.get("errors", [])
    if errors:
        logger.error(
            f"PVWatts API returned errors for lat: {lat}, lon: {lon} due to: {errors}"
        )
        return None, status.HTTP_422_UNPROCESSABLE_ENTITY

    # # Extract inputs (echoed back from the API response)
    # inputs = data.get("inputs", {})
    
    # Extract station info fields
    station_info = data.get("station_info", {})
    station_lat = station_info.get("lat")
    station_lon = station_info.get("lon")
    elevation = station_info.get("elev")
    timezone = station_info.get("tz")
    location = station_info.get("location")
    city = station_info.get("city")
    state = station_info.get("state")
    solar_resource_file = station_info.get("solar_resource_file")
    distance = station_info.get("distance")
    weather_data_source = station_info.get("weather_data_source")

    # Extract output fields
    outputs = data.get("outputs", {})
    ac_annual = outputs.get("ac_annual")
    solrad_annual = outputs.get("solrad_annual")
    capacity_factor = outputs.get("capacity_factor")
    ac_monthly = outputs.get("ac_monthly")
    solrad_monthly = outputs.get("solrad_monthly")
    poa_monthly = outputs.get("poa_monthly")
    dc_monthly = outputs.get("dc_monthly")

    # Create and return PVWattsCalculation
    return PVWattsCalculation(
        latitude=lat,
        longitude=lon,
        system_capacity=system_capacity,
        module_type=module_type,
        losses=losses,
        array_type=array_type,
        tilt=tilt,
        azimuth=azimuth,
        file_id=file_id,
        dataset=dataset,
        radius=radius,
        timeframe=timeframe,
        dc_ac_ratio=dc_ac_ratio,
        gcr=gcr,
        inv_eff=inv_eff,
        bifaciality=bifaciality,
        albedo=albedo,
        soiling=soiling,
        station_lat=station_lat,
        station_lon=station_lon,
        elevation=elevation,
        timezone=timezone,
        location=location,
        city=city,
        state=state,
        solar_resource_file=solar_resource_file,
        distance=distance,
        weather_data_source=weather_data_source,
        ac_annual=ac_annual,
        solrad_annual=solrad_annual,
        capacity_factor=capacity_factor,
        ac_monthly=ac_monthly,
        solrad_monthly=solrad_monthly,
        poa_monthly=poa_monthly,
        dc_monthly=dc_monthly,
    ), status.HTTP_200_OK

