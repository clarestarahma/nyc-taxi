from prefect import task, flow, get_run_logger
from nyc_taxi.utils.db_utils import execute_query
from nyc_taxi.queries.taxi_queries import TaxiQueries
import pandas as pd

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


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
# TASK: CREATE TABLE
# =========================
@task(name="Create Taxi Table")
def create_table_if_not_exists(table_name: str, sample_url: str, schema: str):
    logger = get_run_logger()
    target_table = f"{schema}.{table_name}"

    execute_query(query=f"CREATE SCHEMA IF NOT EXISTS {schema}", df=None)

    query = f"""
    CREATE TABLE IF NOT EXISTS {target_table} AS
    SELECT * FROM read_parquet('{sample_url}')
    LIMIT 0
    """
    execute_query(query=query, df=None)

    logger.info(f"✅ Table ready: {target_table}")


# =========================
# TASK: INGEST 1 FILE
# =========================
@task(name="Ingest Single Parquet", retries=3, retry_delay_seconds=10)
def ingest_single_parquet(table_name: str, schema: str, url: str):
    logger = get_run_logger()
    target_table = f"{schema}.{table_name}"

    logger.info(f"📥 Ingesting {url}")

    df = pd.read_parquet(url)
    execute_query(query=TaxiQueries.INSERT.format(target_table=target_table), df=df)

    logger.info(f"✅ Done: {url}")


# =========================
# FLOW: INGEST PER TAXI TYPE
# =========================
@flow(name="Ingest Taxi Parquet Per Type")
def ingest_taxi_type(taxi_type: str, table_name: str, year: int, months: list[int]):
    logger = get_run_logger()
    schema = "bronze"

    urls = generate_urls(taxi_type, year, months)

    if not urls:
        raise ValueError("❌ No URLs generated")

    logger.info(f"🚀 Start ingest {taxi_type} taxi ({year})")

    # create table pakai file pertama
    create_table_if_not_exists(table_name, urls[0], schema)

    # ingest semua file
    for url in urls:
        ingest_single_parquet(table_name, schema, url)

    logger.info(f"🎉 Finished ingest {taxi_type}")


# =========================
# MAIN FLOW
# =========================
@flow(name="Ingest All Taxi Parquet")
def ingest_all_taxi_parquet():
    months = [1, 2, 3, 4]  # tinggal extend nanti
    taxi_type = {"yellow": "yellow_taxi", "green": "green_taxi"}
    
    try:
        for type, table_name in taxi_type.items():
            ingest_taxi_type(type, table_name, 2025, months)
    except KeyboardInterrupt:
        raise