import os
from dotenv import load_dotenv

load_dotenv()

DOMAIN = "data.cityofnewyork.us"

# Rentang waktu yang mau diambil
START_DATE = "2023-01-01T00:00:00"
END_DATE   = "2023-04-30T23:59:59"

# Daftar target dataset dengan metadata-nya
TARGET_DATASETS = {
    "yellow_taxi": {
        "dataset_id": "tg2q-qycn",
        "time_column": "tpep_pickup_datetime"
    },
    "green_taxi": {
        "dataset_id": "peyi-gg4n",
        "time_column": "lpep_pickup_datetime"
    },
    "fhv_taxi": {
        "dataset_id": "ywip-y6qr",
        "time_column": "pickup_datetime"
    },
    "hvfhv_taxi": {
        "dataset_id": "u253-aew4",
        "time_column": "pickup_datetime"
    }
}

# Kredensial dari .env
APP_TOKEN = os.getenv("APP_TOKEN")
USERNAME = os.getenv("USERNAME_OPENDATA")
PASSWORD = os.getenv("PASSWORD_OPENDATA")

# Filter Default
DEFAULT_LIMIT = 50000

RAW_DB_PATH = "data/nyc_taxi.db"