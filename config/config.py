import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

GEOCODING_SERVICE_URL = os.getenv("GEOCODING_SERVICE_URL", "https://nominatim.openstreetmap.org/search")
APP_USER_AGENT = os.getenv("APP_USER_AGENT", "solar-resource-explorer-v1.0")

NREL_API_KEY = os.getenv("NREL_API_KEY")
NREL_SOLAR_RESOURCE_URL = os.getenv("NREL_SOLAR_RESOURCE_URL", "https://developer.nlr.gov/api/solar/solar_resource/v1")

NREL_PVWATTS_URL = os.getenv("NREL_PVWATTS_URL", "https://developer.nrel.gov/api/pvwatts/v8")