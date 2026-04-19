import pandas as pd
from nyc_taxi.config import settings
from nyc_taxi.utils.db_utils import execute_query
import logging
import sys
from prefect import task, flow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def preprocess_data():
    """
    Fungsi untuk membersihkan data mentah menggunakan SQL/DuckDB.
    """
    logger = logging.getLogger(__name__)
    logger.info("🧹 [02_PREPROCESSING] Memulai pembersihan data...")
    
    """
    FUNCTION FOR PREPROCESSING
    """
    # =========================
    # CREATING SCHEMA SILVER
    # =========================
    execute_query("CREATE SCHEMA IF NOT EXISTS silver")
    logger.info("✅ Schema silver siap.")


    # =========================
    # CLEANING: WEATHER
    # =========================
    logger.info("☁️ Memulai cleaning weather data...")
    query_weather = """
    CREATE OR REPLACE TABLE silver.weather AS
    SELECT
        CAST(date AS DATE) AS date,
        COALESCE(temperature_max, 0)::FLOAT AS temperature_max,
        COALESCE(temperature_min, 0)::FLOAT AS temperature_min,
        COALESCE(precipitation, 0)::FLOAT AS precipitation,
        COALESCE(wind_speed_max, 0)::FLOAT AS windspeed_max,
        COALESCE(weather_code, 0)::INTEGER AS weathercode,

        -- mapping weather category
        CASE
            WHEN weather_code IN (0,1) THEN 'clear'
            WHEN weather_code IN (2,3) THEN 'partly cloudy'
            WHEN weather_code IN (45,48) THEN 'fog'
            WHEN weather_code BETWEEN 51 AND 67 THEN 'rain'
            WHEN weather_code BETWEEN 71 AND 77 THEN 'snow fall'
            ELSE 'other'
        END AS weather_category

    FROM bronze.weather
    """

    execute_query(query_weather)
    logger.info("✅ Cleaning weather selesai dan disimpan ke silver.weather.")

# =========================
# CHECKING & SHOWING CLEANED DATA
# =========================

@task(name="Show per Table")
def show_table(table_name):
    logger = logging.getLogger(__name__)
    try:
        df = execute_query(f"SELECT * FROM silver.{table_name}")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        logger.info(f"✅ Data berhasil dimuat ke DataFrame!")

        print(f"Data {table_name}".capitalize())
        print(f"Shape: {df.shape}")
        print(df.head(), "\n")
    except Exception as e:
        logger.error(f"Gagal menampilkan data: {e}")


# @flow(name="Show All Silver Table", log_prints=True)
def show_silver_tables():
    tables = ["yellow_trips", "green_trips", "weather"]
    
    for table in tables:
        df = execute_query(f"SELECT * FROM silver.{table} LIMIT 5")
        print(f"\n=== {table} ===")
        print(df)

if __name__ == "__main__":
    # Cek apakah ada argumen 'show' pas manggil
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_silver_tables()
    else:
        preprocess_data() # main function