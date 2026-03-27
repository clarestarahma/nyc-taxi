import duckdb
import pandas as pd
from nyc_taxi.config import settings
from nyc_taxi.utils.duckdb import query_to_df
import logging
import sys
from prefect import task, flow

def preprocess_data():
    """
    Fungsi untuk membersihkan data mentah menggunakan SQL/DuckDB.
    """
    logger = logging.getLogger(__name__)
    logger.info("🧹 [02_PREPROCESSING] Memulai pembersihan data...")
    
    """
    FUNCTION FOR PREPROCESSING
    """       
    
    print("✅ [02_PREPROCESSING] Data telah bersih dan siap untuk disimpan.")

@task(name="Show per Table")
def show_table(table_name):
    logger = logging.getLogger(__name__)
    try:
        df = query_to_df(f"SELECT * FROM raw.{table_name}")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        logger.info(f"✅ Data berhasil dimuat ke DataFrame!")

        print(f"Data {table_name}".capitalize())
        print(f"Shape: {df.shape}")
        print(df.head(), "\n")
    except Exception as e:
        logger.error(f"Gagal menampilkan data: {e}")


@flow(name="Show All Raw Table", log_prints=True)
def show_all_raw_table():
    for table_name, _ in settings.TARGET_DATASETS.items():
        show_table(table_name=table_name)

if __name__ == "__main__":
    # Cek apakah ada argumen 'show' pas manggil
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_all_raw_table()
    else:
        preprocess_data() # main function