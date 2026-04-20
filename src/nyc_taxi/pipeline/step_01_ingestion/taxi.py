from prefect import task, flow, get_run_logger
from nyc_taxi.utils.db_utils import execute_query
from nyc_taxi.queries.taxi_queries import TaxiQueries
import pandas as pd

from prefect import task, flow, get_run_logger
from nyc_taxi.queries.taxi_queries import TaxiQueries
import requests
from pathlib import Path

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

ROOT_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"


# =========================
# HELPER: GENERATE URL
# =========================
def generate_urls(taxi_type: str, year: int, months: list[int]):
    urls = []
    for month in months:
        mm = str(month).zfill(2)
        url = f"{BASE_URL}/{taxi_type}_tripdata_{year}-{mm}.parquet"
        urls.append(url)
    return urls

# =========================
# TASK: INGEST 1 FILE
# =========================
@task(name="Ingest Single Parquet", retries=3, retry_delay_seconds=10)
def ingest_single_parquet(url: str):
    logger = get_run_logger()

    logger.info(f"📥 Ingesting {url}")

    response = requests.get(url)
    response.raise_for_status()
    
    #ambil nama file dari url
    file_name = url.split('/')[-1]

    #make directory
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    filepath = BRONZE_DIR / file_name

    #saving parquet file
    with open(filepath, "wb") as file:
        file.write(response.content)

    logger.info(f"✅ Parquet file {file_name} saved to {filepath}")


# =========================
# FLOW: INGEST PER TAXI TYPE
# =========================
@flow(name="Ingest Taxi Parquet Per Type")
def ingest_taxi_type(taxi_type: str, year: int, months: list[int]):
    logger = get_run_logger()

    urls = generate_urls(taxi_type, year, months)

    if not urls:
        raise ValueError("❌ No URLs generated")

    logger.info(f"🚀 Start ingest {taxi_type} taxi ({year})")

    # ingest semua file
    for url in urls:
        ingest_single_parquet(url)

    logger.info(f"🎉 Finished ingest {taxi_type}")


# =========================
# MAIN FLOW
# =========================
@flow(name="Ingest All Taxi Parquet")
def ingest_all_taxi_parquet():
    months = [1, 2, 3, 4]  # tinggal extend nanti
    taxi_type = {"yellow": "yellow_taxi", "green": "green_taxi"}
    
    try:
        for type, _ in taxi_type.items():
            ingest_taxi_type(type, 2025, months)
    except KeyboardInterrupt:
        raise