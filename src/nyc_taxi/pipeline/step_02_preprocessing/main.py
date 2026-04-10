import pandas as pd
from nyc_taxi.config import settings
from nyc_taxi.utils.db_utils import query_to_df
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
    # =========================
    # CREATING SCHEMA SILVER
    # =========================
    query_to_df("CREATE SCHEMA IF NOT EXISTS silver")

    # =========================
    # CLEANING: YELLOW TAXI
    # =========================
    query_yellow = """
    CREATE OR REPLACE TABLE silver.yellow_trips AS
    SELECT
        CAST(tpep_pickup_datetime AS TIMESTAMP) AS tpep_pickup_datetime,
        CAST(tpep_dropoff_datetime AS TIMESTAMP) AS tpep_dropoff_datetime,
        CAST(PULocationID AS INTEGER) AS pulocationid,
        CAST(DOLocationID AS INTEGER) AS dolocationid,

        COALESCE(trip_distance, 0)::FLOAT AS trip_distance,
        COALESCE(fare_amount, 0)::FLOAT AS fare_amount,
        COALESCE(tip_amount, 0)::FLOAT AS tip_amount,
        COALESCE(total_amount, 0)::FLOAT AS total_amount,
        COALESCE(passenger_count, 1)::INTEGER AS passenger_count,

        -- duration
        (epoch(tpep_dropoff_datetime) - epoch(tpep_pickup_datetime))/60 AS trip_duration_min

    FROM bronze.yellow_taxi
    WHERE
        tpep_pickup_datetime IS NOT NULL
        AND tpep_dropoff_datetime IS NOT NULL
        AND tpep_dropoff_datetime > tpep_pickup_datetime
    """

    query_to_df(query_yellow)


    # =========================
    # CLEANING: GREEN TAXI
    # =========================
    query_green = """
    CREATE OR REPLACE TABLE silver.green_trips AS
    SELECT
        CAST(lpep_pickup_datetime AS TIMESTAMP) AS lpep_pickup_datetime,
        CAST(lpep_dropoff_datetime AS TIMESTAMP) AS lpep_dropoff_datetime,
        CAST(PULocationID AS INTEGER) AS pulocationid,
        CAST(DOLocationID AS INTEGER) AS dolocationid,

        COALESCE(trip_distance, 0)::FLOAT AS trip_distance,
        COALESCE(fare_amount, 0)::FLOAT AS fare_amount,
        COALESCE(tip_amount, 0)::FLOAT AS tip_amount,
        COALESCE(total_amount, 0)::FLOAT AS total_amount,
        COALESCE(passenger_count, 1)::INTEGER AS passenger_count,

        (epoch(lpep_dropoff_datetime) - epoch(lpep_pickup_datetime))/60 AS trip_duration_min

    FROM bronze.green_taxi
    WHERE
        lpep_pickup_datetime IS NOT NULL
        AND lpep_dropoff_datetime IS NOT NULL
        AND lpep_dropoff_datetime > lpep_pickup_datetime
    """

    query_to_df(query_green)


    # =========================
    # REMOVING OUTLIER
    # =========================
    query_outlier_yellow = """
    DELETE FROM silver.yellow_trips
    WHERE trip_distance <= 0
    OR fare_amount < 0
    OR total_amount < 0
    OR trip_duration_min <= 0
    OR trip_duration_min > 180
    """

    query_to_df(query_outlier_yellow)

    query_outlier_green = """
    DELETE FROM silver.green_trips
    WHERE trip_distance <= 0
    OR fare_amount < 0
    OR total_amount < 0
    OR trip_duration_min <= 0
    OR trip_duration_min > 180
    """

    query_to_df(query_outlier_green)


    # =========================
    # CLEANING: WEATHER
    # =========================
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

    query_to_df(query_weather)

    print("✅ [02_PREPROCESSING] Data telah bersih dan siap untuk disimpan.")

# =========================
# CHECKING & SHOWING CLEANED DATA
# =========================

@task(name="Show per Table")
def show_table(table_name):
    logger = logging.getLogger(__name__)
    try:
        df = query_to_df(f"SELECT * FROM silver.{table_name}")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        logger.info(f"✅ Data berhasil dimuat ke DataFrame!")

        print(f"Data {table_name}".capitalize())
        print(f"Shape: {df.shape}")
        print(df.head(), "\n")
    except Exception as e:
        logger.error(f"Gagal menampilkan data: {e}")


@flow(name="Show All Silver Table", log_prints=True)
def show_silver_tables():
    tables = ["yellow_trips", "green_trips", "weather"]
    
    for table in tables:
        df = query_to_df(f"SELECT * FROM silver.{table} LIMIT 5")
        print(f"\n=== {table} ===")
        print(df)

if __name__ == "__main__":
    # Cek apakah ada argumen 'show' pas manggil
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_silver_tables()
    else:
        preprocess_data() # main function