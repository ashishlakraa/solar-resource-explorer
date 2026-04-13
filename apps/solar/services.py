from __future__ import annotations

from dataclasses import dataclass
import logging
import requests
from rest_framework import status

from config.config import NREL_SOLAR_RESOURCE_URL, NREL_API_KEY, NREL_PVWATTS_URL

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class PVWattsCalculation:
    latitude: float
    longitude: float
    system_capacity: float
    module_type: int
    losses: float
    array_type: int
    tilt: float
    azimuth: float
    
    # Optional parameters
    file_id: str = None
    dataset: str = None
    radius: int = None
    timeframe: str = None
    dc_ac_ratio: float = None
    gcr: float = None
    inv_eff: float = None
    bifaciality: float = None
    albedo: float = None
    soiling: str = None
    
    # Response outputs
    ac_annual: float = None
    solrad_annual: float = None
    capacity_factor: float = None
    ac_monthly: list = None
    solrad_monthly: list = None


@dataclass(frozen=True)
class SolarResourceReading:
    latitude: float
    longitude: float
    
    # Annual data
    annual_avg_dni: float
    annual_avg_ghi: float
    annual_avg_lat_tilt: float
    
    # Monthly data
    monthly_avg_dni: dict
    monthly_avg_ghi: dict
    monthly_avg_lat_tilt: dict



def fetch_solar_resource_data(latitude: float, longitude: float) -> SolarResourceReading:
    """Fetch solar resource data from NREL API and return SolarResourceReading."""

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
    if data.get("error"):
        logger.error(f"API error occurred for lat: {latitude}, lon: {longitude}: {data.get('error')}")
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
    soiling: str = None,
) -> tuple:
    """Fetch PVWatts calculation from NREL API and return PVWattsCalculation."""

    api_url = f"{NREL_PVWATTS_URL}.json"

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
    }

    # Add optional parameters if provided
    if file_id is not None:
        payload["file_id"] = file_id
    if dataset is not None:
        payload["dataset"] = dataset
    if radius is not None:
        payload["radius"] = radius
    if timeframe is not None:
        payload["timeframe"] = timeframe
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
            f"PVWatts API returned errors for lat: {lat}, lon: {lon}: {errors}"
        )
        return None, status.HTTP_422_UNPROCESSABLE_ENTITY

    # Extract inputs
    inputs = data.get("inputs", {})
    response_lat = float(inputs.get("lat", lat))
    response_lon = float(inputs.get("lon", lon))
    response_system_capacity = float(inputs.get("system_capacity", system_capacity))
    response_module_type = int(inputs.get("module_type", module_type))
    response_losses = float(inputs.get("losses", losses))
    response_array_type = int(inputs.get("array_type", array_type))
    response_tilt = float(inputs.get("tilt", tilt))
    response_azimuth = float(inputs.get("azimuth", azimuth))

    # Extract optional parameters from response
    response_file_id = inputs.get("file_id")
    response_dataset = inputs.get("dataset")
    response_radius = inputs.get("radius")
    response_timeframe = inputs.get("timeframe")
    response_dc_ac_ratio = inputs.get("dc_ac_ratio")
    response_gcr = inputs.get("gcr")
    response_inv_eff = inputs.get("inv_eff")
    response_bifaciality = inputs.get("bifaciality")
    response_albedo = inputs.get("albedo")
    response_soiling = inputs.get("soiling")

    # Extract outputs
    outputs = data.get("outputs", {})
    ac_annual = outputs.get("ac_annual")
    solrad_annual = outputs.get("solrad_annual")
    capacity_factor = outputs.get("capacity_factor")
    ac_monthly = outputs.get("ac_monthly")
    solrad_monthly = outputs.get("solrad_monthly")

    # Create and return PVWattsCalculation
    return PVWattsCalculation(
        latitude=response_lat,
        longitude=response_lon,
        system_capacity=response_system_capacity,
        module_type=response_module_type,
        losses=response_losses,
        array_type=response_array_type,
        tilt=response_tilt,
        azimuth=response_azimuth,
        file_id=response_file_id,
        dataset=response_dataset,
        radius=response_radius,
        timeframe=response_timeframe,
        dc_ac_ratio=response_dc_ac_ratio,
        gcr=response_gcr,
        inv_eff=response_inv_eff,
        bifaciality=response_bifaciality,
        albedo=response_albedo,
        soiling=response_soiling,
        ac_annual=ac_annual,
        solrad_annual=solrad_annual,
        capacity_factor=capacity_factor,
        ac_monthly=ac_monthly,
        solrad_monthly=solrad_monthly,
    ), status.HTTP_200_OK

