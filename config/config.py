import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

GEOCODING_SERVICE_URL = os.getenv("GEOCODING_SERVICE_URL", "https://nominatim.openstreetmap.org")
APP_USER_AGENT = os.getenv("APP_USER_AGENT", "solar-resource-explorer-1.0")

