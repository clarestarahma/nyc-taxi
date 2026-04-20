import requests
import pandas as pd
import json
from prefect import task, flow, get_run_logger
<<<<<<< Updated upstream
from nyc_taxi.utils.db_utils import save_to_db
=======
>>>>>>> Stashed changes
from nyc_taxi.config.settings import (
    STATIC_DIR,
    WEATHER_API_URL,
    NYC_LATITUDE,
    NYC_LONGITUDE,
    WEATHER_DAILY_FIELDS,
    START_DATE,
    END_DATE
)

# =========================
# TASK 1: FETCH DATA
# =========================
@task(name="Fetch Weather Data", retries=3, retry_delay_seconds=5)
def fetch_weather_data():
    logger = get_run_logger()
    
    url = WEATHER_API_URL
    params = {
        "latitude": NYC_LATITUDE,
        "longitude": NYC_LONGITUDE,
        "start_date": START_DATE[:10],
        "end_date": END_DATE[:10],
        "daily": ",".join(WEATHER_DAILY_FIELDS),
        "timezone": "America/New_York"
    }

    logger.info(f"📡 Fetching weather data from {url} with params: {params}")

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch weather data: {response.status_code} - {response.text}")
    
    return response.json()

# =========================
# TASK 2: SAVE RAW JSON
# =========================
@task(name="Save Raw Weather JSON to data/static")
def save_raw_weather_json(data: dict):
    logger = get_run_logger()
    
    try:
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
        file_path = STATIC_DIR / "weather_raw.json"

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Raw weather JSON saved to {file_path.resolve()}")
    except Exception as e:
        logger.error(f"❌ Failed to save raw weather JSON to {file_path}: {e}")
        raise

# # =========================
# # TASK 3: TRANSFORM
# # =========================
# @task(name="Transform Weather Data")
# def transform_weather_data(data: dict) -> pd.DataFrame:
#     logger = get_run_logger()
    
#     daily = data.get("daily", {})

#     df = pd.DataFrame({
#         "date": pd.to_datetime(daily.get("time")),
#         "temperature_max": daily.get("temperature_2m_max"),
#         "temperature_min": daily.get("temperature_2m_min"),
#         "precipitation": daily.get("precipitation_sum"),
#         "wind_speed_max": daily.get("windspeed_10m_max"),
#         "weather_code": daily.get("weathercode")
#     })

#     logger.info(f"✅ Weather data transformed into DataFrame with {len(df)} records.")

#     return df

# =========================
# TASK 4: SAVE
# =========================
@task(name="Save Weather Data to data/static")
def save_weather_data(df: pd.DataFrame):
    logger = get_run_logger()
    
<<<<<<< Updated upstream
    try: 
        save_to_db(df=df, table_name="weather", schema="bronze")
        logger.info("✅ Weather data saved to DuckDB successfully.")
=======
    try:
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
        file_path = STATIC_DIR / "weather.csv"
        df.to_csv(file_path, index=False, encoding="utf-8")

        logger.info(f"✅ Weather data saved to {file_path.resolve()}")
>>>>>>> Stashed changes
    except Exception as e:
        logger.error(f"❌ Failed to save weather data to {file_path}: {e}")
        raise

# =========================
# MAIN FLOWS
# =========================
@flow(name="Ingest Weather Data")
def ingest_weather_data():
    weather_json = fetch_weather_data()
    save_raw_weather_json(weather_json)

@flow(name="Ingest Raw Weather JSON")
def ingest_raw_weather_json():
    weather_json = fetch_weather_data()
    save_raw_weather_json(weather_json)