from prefect import task, flow, get_run_logger
from nyc_taxi.utils.db_utils import execute_query
from nyc_taxi.queries.taxi_queries import TaxiQueries
import pandas as pd

from prefect import task, flow, get_run_logger
from nyc_taxi.queries.taxi_queries import TaxiQueries
import requests
from pathlib import Path
from nyc_taxi.config.settings import ZONE_LOOKUP_URL


ROOT_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT_DIR / "data"
STATIC_DIR = DATA_DIR / "static"

# ==============================
# TASK: INGEST ZONE LOOKUP TABLE
# ==============================
@task(name="Ingest Zone Lookup Table", retries=3, retry_delay_seconds=10)
def ingest_zone_lookup():
    logger = get_run_logger()

    logger.info(f"📥 Ingesting {ZONE_LOOKUP_URL}")

    response = requests.get(ZONE_LOOKUP_URL)
    response.raise_for_status()
    
    #ambil nama file dari url
    file_name = ZONE_LOOKUP_URL.split('/')[-1]

    #make directory
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    filepath = STATIC_DIR / file_name

    #saving parquet file
    with open(filepath, "wb") as file:
        file.write(response.content)

    logger.info(f"✅ Parquet file {file_name} saved to {filepath}")