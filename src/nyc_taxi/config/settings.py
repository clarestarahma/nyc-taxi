import os
from dotenv import load_dotenv

load_dotenv()

DOMAIN = "data.cityofnewyork.us"

# Rentang waktu yang mau diambil
START_DATE = "2025-01-01T00:00:00"
END_DATE   = "2025-04-01T23:59:59"

# Daftar target dataset dengan metadata-nya
TARGET_DATASETS = {
    "yellow_taxi": {
        "dataset_id": "4b4i-vvec",
        "time_column": "tpep_pickup_datetime"
    },
    "green_taxi": {
        "dataset_id": "peyi-gg4n",
        "time_column": "lpep_pickup_datetime"
    }
}

# Kredensial dari .env
APP_TOKEN = os.getenv("APP_TOKEN")
USERNAME = os.getenv("USERNAME_OPENDATA")
PASSWORD = os.getenv("PASSWORD_OPENDATA")

# Filter Default
DEFAULT_LIMIT = 50000

RAW_DB_PATH = "data/nyc_taxi.db"

#

# Weather API
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"

NYC_LATITUDE = 40.7128
NYC_LONGITUDE = -74.0060

WEATHER_DAILY_FIELDS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
    "weathercode"
]