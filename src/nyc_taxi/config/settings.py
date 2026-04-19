import os
from dotenv import load_dotenv

load_dotenv()
from pathlib import Path
import os

# 1. Deteksi ROOT Project (Naik 3 tingkat dari config/settings.py)
# folder: src/nyc_taxi/config/ -> src/nyc_taxi/ -> src/ -> ROOT
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# 2. Tentukan Path Data & DB di ROOT
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "nyc_taxi.db"

DOMAIN = "data.cityofnewyork.us"

# Rentang waktu yang mau diambil
START_DATE = "2025-01-01T00:00:00"
END_DATE   = "2025-04-30T23:59:59"

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

ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

# Kredensial dari .env
APP_TOKEN = os.getenv("APP_TOKEN")
USERNAME = os.getenv("USERNAME_OPENDATA")
PASSWORD = os.getenv("PASSWORD_OPENDATA")

# Filter Default
DEFAULT_LIMIT = 50000

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

#  CLEANING THRESHOLD
LOWER_FARE_YELLOW = 2.50
UPPER_FARE_YELLOW = 300
LOWER_TOTAL_AMOUNT_YELLOW = 3.00
UPPER_TOTAL_AMOUNT_YELLOW = 350
LOWER_TIP_AMOUNT_YELLOW = 0
UPPER_TIP_AMOUNT_YELLOW = 200
LOWER_TRIP_DISTANCE_YELLOW = 0.1
UPPER_TRIP_DISTANCE_YELLOW = 100
LOWER_TRIP_DURATION_MIN_YELLOW = 1
UPPER_TRIP_DURATION_MIN_YELLOW = 180

LOWER_FARE_GREEN = 2.50
UPPER_FARE_GREEN = 200
LOWER_TOTAL_AMOUNT_GREEN = 3.00
UPPER_TOTAL_AMOUNT_GREEN = 250
LOWER_TIP_AMOUNT_GREEN = 0
UPPER_TIP_AMOUNT_GREEN = 150
LOWER_TRIP_DISTANCE_GREEN = 0.1
UPPER_TRIP_DISTANCE_GREEN = 60
LOWER_TRIP_DURATION_MIN_GREEN = 1
UPPER_TRIP_DURATION_MIN_GREEN = 120


DROP_COLUMNS_YELLOW = [
    "VendorID",              # ID vendor taksi, tidak relevan
    "RatecodeID",            # kode tarif, tidak dianalisis
    "store_and_fwd_flag",    # flag koneksi GPS, tidak relevan
    "payment_type",          # tunai/kartu, tidak dianalisis
    "extra",                 # surcharge tambahan, sudah tercakup total_amount
    "mta_tax",               # pajak MTA, tidak dianalisis
    "tolls_amount",          # tol, tidak dianalisis
    "improvement_surcharge", # surcharge, tidak dianalisis
    "congestion_surcharge",  # biaya kemacetan, tidak dianalisis
    "Airport_fee",           # biaya bandara, tidak dianalisis
    "cbd_congestion_fee",    # biaya central business district, tidak dianalisis
]

DROP_COLUMNS_GREEN = [
    "VendorID",              # ID vendor, tidak relevan
    "store_and_fwd_flag",    # flag GPS, tidak relevan
    "RatecodeID",            # kode tarif, tidak dianalisis
    "payment_type",          # tunai/kartu, tidak dianalisis
    "trip_type",             # street-hail vs dispatch, tidak dianalisis
    "extra",                 # surcharge tambahan, tidak dianalisis
    "mta_tax",               # pajak MTA, tidak dianalisis
    "tolls_amount",          # tol, tidak dianalisis
    "improvement_surcharge", # surcharge, tidak dianalisis
    "congestion_surcharge",  # biaya kemacetan, tidak dianalisis
    "cbd_congestion_fee",    # biaya central business district, tidak dianalisis
    "ehail_fee",             # semua null, tidak ada nilainya sama sekali
]