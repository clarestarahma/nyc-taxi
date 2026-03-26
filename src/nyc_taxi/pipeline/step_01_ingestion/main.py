from nyc_taxi.config import settings
from sodapy import Socrata
import pandas as pd
from nyc_taxi.utils.duckdb import save_to_raw
from nyc_taxi.config.settings import TARGET_DATASETS, DOMAIN, START_DATE, END_DATE

def ingest_taxi_data(*, dataset_id: str, table_name: str, time_col: str):
    client = Socrata(
        settings.DOMAIN,
        settings.APP_TOKEN,
        username=settings.USERNAME,
        password=settings.PASSWORD
    )

    current_offset = 0
    total_pulled = 0

    print("🚀 Memulai proses Ingestion Masif (Jan-Apr 2023)...")

    for i in range(2): # ini cuma coba aja, real nya pakai while
    # while True:
        try:
            # Tarik potongan data
            results = client.get(
                dataset_id,
                where=f"{time_col} BETWEEN '{START_DATE}' AND '{END_DATE}'",
                limit=settings.DEFAULT_LIMIT,
                offset=current_offset,
                # order=f"{time_col} ASC" # supaya urut
            )

            if not results:
                print("🏁 Semua data sudah berhasil ditarik!")
                break

            # Ubah ke Pandas & Simpan ke DuckDB
            df = pd.DataFrame.from_records(results)
            save_to_raw(df, table_name=table_name)

            # Update status Progres
            current_offset += len(df)
            total_pulled += len(df)
            print(f"📦 Progress: {total_pulled} baris disimpan ke database...")

        except Exception as e:
            print(f"DEBUG: [{table_name}] ID: {dataset_id} | Col: {time_col}")
            print(f"⚠️ Terjadi gangguan: {e}. Mencoba lagi...")
            # continue # Lanjut lagi kalau error (Self-healing)
            return
        
def ingest_all_taxi_data():
    for table_name, info in TARGET_DATASETS.items():
        print(f"===== Processing {table_name} =====")

        ingest_taxi_data(
            dataset_id=info["dataset_id"],
            table_name=table_name,
            time_col=info["time_column"]
        )

if __name__ == "__main__":
    ingest_all_taxi_data()