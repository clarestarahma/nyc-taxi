from nyc_taxi.config import settings
from sodapy import Socrata
import pandas as pd
from nyc_taxi.utils.duckdb import save_to_raw
from nyc_taxi.config.settings import TARGET_DATASETS, START_DATE, END_DATE
from prefect import task, get_run_logger
import os
import time

# --- TASKS ---

@task(timeout_seconds=600, retries=3, retry_delay_seconds=30, name="Fetch Batch From Socrata")
def fetch_batch(*, client: Socrata, dataset_id: str, table_name: str, time_col: str, offset: int):
    """Function for fetch data from API"""
    logger = get_run_logger()
    logger.info(f"Mengambil data dari offset: {offset}")

    # Tarik potongan data
    results = client.get(
        dataset_id,
        where=f"{time_col} BETWEEN '{START_DATE}' AND '{END_DATE}'",
        limit=settings.DEFAULT_LIMIT,
        offset=offset,
        order=f"{time_col} ASC" # supaya urut
    )
    return results
        
@task(timeout_seconds=600, name="Save Batch to DuckDB")
def save_batch(results, table_name):
    """Function for convert to Pandas and save to DB"""
    if not results:
        return 0
    
    logger = get_run_logger()
    
    # Ubah ke Pandas & Simpan ke DuckDB
    try:
        df = pd.DataFrame.from_records(results)
        save_to_raw(df, table_name=table_name, schema="raw_taxi")
        return len(df)
    except Exception as e:
        logger.error(f"❌ Gagal menyimpan ke {table_name}: {e}")
        return 0

@task(name="Ingest Per Taxi Type")        
def ingest_taxi_data(dataset_id: str, table_name: str, time_col:str):
    logger = get_run_logger()
    """Sub Flow for one type of taxi"""
    client = Socrata(
        settings.DOMAIN,
        settings.APP_TOKEN,
        username=settings.USERNAME,
        password=settings.PASSWORD
    )

    current_offset = 0
    total_pulled = 0

    logger.info("🚀 Memulai proses Ingestion Masif (Jan-Apr 2023)...")

    while True:
        try:
            # for _ in range(1): # ini cuma coba aja, real nya pakai while
            while True:
                results = fetch_batch(client=client, dataset_id=dataset_id, table_name=table_name, time_col=time_col, offset=current_offset)
                    
                if not results:
                    logger.info(f"🏁 {table_name} selesai ditarik!")
                    break

                count = save_batch(results, table_name)

                if count is None:
                    logger.error(f"🛑 Menghentikan {table_name} karena error database.")
                    break

                current_offset += count
                total_pulled += count
                logger.info(f"📦 Batch selesai. Total sementara: {total_pulled}")
                time.sleep(0.5)
            logger.info(f"📦 Progress {table_name}: {total_pulled} baris...")
            break

        except KeyboardInterrupt:
            raise


def ingest_all_taxi_data():
    """Main Flow that regulates all types of taxis"""
    try:
        for table_name, info in TARGET_DATASETS.items():
            print(f"===== Processing {table_name} =====")

            ingest_taxi_data(
                dataset_id=info["dataset_id"],
                table_name=table_name,
                time_col=info["time_column"]
            )
    except KeyboardInterrupt:
        print("\n[!] INTERRUPT DITERIMA. Mematikan sistem...")
        os._exit(0)

if __name__ == "__main__":
    ingest_all_taxi_data()