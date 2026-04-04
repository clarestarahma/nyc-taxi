import requests
import pandas as pd
from prefect import task, flow, get_run_logger
from nyc_taxi.utils.db_utils import save_to_raw
from nyc_taxi.config.settings import (
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
# TASK 2: TRANSFORM
# =========================
@task(name="Transform Weather Data")
def transform_weather_data(data: dict) -> pd.DataFrame:
    logger = get_run_logger()
    
    daily = data.get("daily", {})

    df = pd.DataFrame({
        "date": pd.to_datetime(daily.get("time")),
        "temperature_max": daily.get("temperature_2m_max"),
        "temperature_min": daily.get("temperature_2m_min"),
        "precipitation": daily.get("precipitation_sum"),
        "wind_speed_max": daily.get("windspeed_10m_max"),
        "weather_code": daily.get("weathercode")
    })

    logger.info(f"✅ Weather data transformed into DataFrame with {len(df)} records.")

    return df

# =========================
# TASK 3: SAVE
# =========================
@task(name="Save Weather Data to DuckDB")
def save_weather_data(df: pd.DataFrame):
    logger = get_run_logger()
    
    try: 
        save_to_raw(df=df, table_name="weather", schema="bronze")
        logger.info("✅ Weather data saved to DuckDB successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to save weather data to DuckDB: {e}")
        raise

# =========================
# MAIN FLOW
# =========================
@flow(name="Ingest Weather Data")
def ingest_weather_data():
    weather_json = fetch_weather_data()
    weather_df = transform_weather_data(weather_json)
    save_weather_data(weather_df)