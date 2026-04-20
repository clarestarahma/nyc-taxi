import pandas as pd
import json
import duckdb
from nyc_taxi.config import settings
from nyc_taxi.config.settings import STATIC_DIR
from nyc_taxi.config.settings import DATABASE_PATH
from nyc_taxi.utils.db_utils import execute_query
import logging
import sys
from prefect import task, flow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def read_weather_json():
    logger = logging.getLogger(__name__)
    file_path = STATIC_DIR / "weather_raw.json"
    
    if not file_path.exists():
        logger.error(f"❌ File {file_path} tidak ditemukan. Pastikan data sudah di-fetch dan disimpan.")
        raise FileNotFoundError(f"File {file_path} tidak ditemukan.")
    
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"✅ Raw weather JSON berhasil dibaca dari {file_path.resolve()}")
        return data
    except Exception as e:
        logger.error(f"❌ Gagal membaca raw weather JSON dari {file_path}: {e}")
        raise

def transform_weather_data(data: dict) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    try:
        daily_data = data.get("daily", {})
        df = pd.DataFrame({
            "date": pd.to_datetime(daily_data.get("time")),
            "temperature_max": daily_data.get("temperature_2m_max"),
            "temperature_min": daily_data.get("temperature_2m_min"),
            "precipitation": daily_data.get("precipitation_sum"),
            "wind_speed_max": daily_data.get("windspeed_10m_max"),
            "weather_code": daily_data.get("weathercode")
        })
        logger.info(f"✅ Raw weather JSON berhasil diubah menjadi DataFrame dengan shape {df.shape}")
        return df
    except Exception as e:
        logger.error(f"❌ Gagal mengubah raw weather JSON menjadi DataFrame: {e}")
        raise

def load_weather_to_silver(df: pd.DataFrame):
    logger = logging.getLogger(__name__)
    try:
        execute_query("CREATE SCHEMA IF NOT EXISTS silver")
        query = "CREATE OR REPLACE TABLE silver.weather AS SELECT * FROM df"
        
        with duckdb.connect(database=DATABASE_PATH) as conn:
            conn.register("df", df)
            conn.execute(query)

        logger.info("✅ Weather data berhasil dimuat ke silver.weather.")
    except Exception as e:
        logger.error(f"❌ Gagal memuat weather data ke silver.weather: {e}")
        raise

def preprocess_data():
    """
    Fungsi untuk membersihkan data mentah menggunakan SQL/DuckDB.
    """
    logger = logging.getLogger(__name__)
    logger.info("🧹 [02_PREPROCESSING] Memulai pembersihan data...")
    
    """
    FUNCTION FOR PREPROCESSING
    """
    logger.info("Membaca raw weather JSON...")
    weather_json = read_weather_json()
    weather_df = transform_weather_data(weather_json)
    # =========================
    # CREATING SCHEMA SILVER
    # =========================
    logger.info("Memulai cleaning dan loading data ke silver...")
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

    FROM df
    """
    with duckdb.connect(database=DATABASE_PATH) as conn:
        conn.register("df", weather_df)
        conn.execute(query_weather)

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