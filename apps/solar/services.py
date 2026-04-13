from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IrradianceReading:
    latitude: float
    longitude: float
    annual_ghi_kwh_m2: float | None = None
    annual_dni_kwh_m2: float | None = None
    annual_dhi_kwh_m2: float | None = None


def fetch_irradiance(latitude: float, longitude: float) -> IrradianceReading:
    """Placeholder solar resource lookup for future NREL integration."""
    return IrradianceReading(latitude=latitude, longitude=longitude)


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
