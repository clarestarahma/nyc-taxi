from nyc_taxi.config.settings import *
from nyc_taxi.utils.db_utils import execute_query, save_to_db

from prefect.logging import get_run_logger
from prefect import task
from pathlib import Path
import pandas as pd
import logging
import os


logger_py = logging.getLogger("nyc_taxi")
logger_py.setLevel(logging.INFO)
ROOT_DIR = Path(__file__).resolve().parents[5]
DATA_DIR = ROOT_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"

@task(name='Read yellow taxi parquet', retries=3, retry_delay_seconds=10)
def df_yellow_taxi_data():
    logger = get_run_logger()
    logger.info('Read yellow taxi parquet')
    df = pd.read_parquet(f'{BRONZE_DIR}/yellow_tripdata_2025-01.parquet')
    yellow_02 = pd.read_parquet(f'{BRONZE_DIR}/yellow_tripdata_2025-02.parquet')
    yellow_03 = pd.read_parquet(f'{BRONZE_DIR}/yellow_tripdata_2025-03.parquet')
    yellow_04 = pd.read_parquet(f'{BRONZE_DIR}/yellow_tripdata_2025-04.parquet')

    yellow_df_list = [df, yellow_02, yellow_03, yellow_04]
    logger.info('Returning yellow taxi parquet')
    return yellow_df_list


def df_green_taxi_data():
    logger_py.info('Read green taxi parquet')
    green_01 = pd.read_parquet(f'{BRONZE_DIR}/green_tripdata_2025-01.parquet')
    green_02 = pd.read_parquet(f'{BRONZE_DIR}/green_tripdata_2025-02.parquet')
    green_03 = pd.read_parquet(f'{BRONZE_DIR}/green_tripdata_2025-03.parquet')
    green_04 = pd.read_parquet(f'{BRONZE_DIR}/green_tripdata_2025-04.parquet')

    green_df_list = [green_01, green_02, green_03, green_04]
    logger_py.info('Returning green taxi parquet')
    return green_df_list


def drop_columns(df_list: list, drop_cols: list):
    for df in df_list:
        df.drop(columns=drop_cols, axis=1, inplace=True)

# drop unused column for yellow and green taxi
@task(name='Drop unused column for yellow and green taxi', retries=3, retry_delay_seconds=10)
def drop_unused_columns(yellow_df_list: list, green_df_list: list, drop_cols_yellow: list, drop_cols_green: list):
    logger = get_run_logger()
    logger.info('Start drop unused columns')
    drop_columns(yellow_df_list, drop_cols_yellow)
    drop_columns(green_df_list, drop_cols_green)
    logger.info('Finish drop unused columns')

# Add trip_duration_min for yellow
def add_yellow_trip_duration_min(df_list: list):
    for df in df_list:
        df['trip_duration_min'] = ((df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60).round(2)

# Add trip_duration_min for green
def add_green_trip_duration_min(df_list: list):
    for df in df_list:
        df['trip_duration_min'] = ((df['lpep_dropoff_datetime'] - df['lpep_pickup_datetime']).dt.total_seconds() / 60).round(2)

#  Add trip doration to yellow and green taxi
@task(name='Add trip duration to yellow and green taxi', retries=3, retry_delay_seconds=10)
def add_trip_duration_min_to_all(yellow_df_list: list, green_df_list: list):
    logger = get_run_logger()
    logger.info('Start add trip duration min column')
    add_yellow_trip_duration_min(yellow_df_list)
    add_green_trip_duration_min(green_df_list)
    logger.info('Finish add trip duration min column')


# CLEANING YELLOW
def cleaning_yellow_taxi(df_list: list):
    for i, df in enumerate(df_list):
        logger_py.info(f"Total awal: {df.shape[0]:,} baris")

        # Isi null passenger_count dengan median
        median_pax = df['passenger_count'].median()
        df['passenger_count'] = df['passenger_count'].fillna(median_pax)
        logger_py.info(f"passenger_count null diisi median: {median_pax}")

        # AMBIL DATA BERSIH
        kondisi_hapus = (
            (df['passenger_count'] > 0) &
            (df['fare_amount'].between(LOWER_FARE_YELLOW, UPPER_FARE_YELLOW)) &
            (df['total_amount'].between(LOWER_TOTAL_AMOUNT_YELLOW, UPPER_TOTAL_AMOUNT_YELLOW)) &
            (df['tip_amount'].between(LOWER_TIP_AMOUNT_YELLOW, UPPER_TIP_AMOUNT_YELLOW)) &
            (df['trip_distance'].between(LOWER_TRIP_DISTANCE_YELLOW, UPPER_TRIP_DISTANCE_YELLOW)) &
            (df['trip_duration_min'].between(LOWER_TRIP_DURATION_MIN_YELLOW, UPPER_TRIP_DURATION_MIN_YELLOW))
        )
        df_clean = df[kondisi_hapus].copy()
        df_list[i] = df_clean
        logger_py.info(f"Setelah hapus anomali: {df_clean.shape[0]:,} baris")
        logger_py.info(f"Dihapus: {df.shape[0] - df_clean.shape[0]:,} baris")


# CLEANING GREEN
def cleaning_green_taxi(df_list: list):
    for i, df in enumerate(df_list):
        logger_py.info(f"Total awal: {df.shape[0]:,} baris")

        # Isi null passenger_count dengan median
        median_pax = df['passenger_count'].median()
        df['passenger_count'] = df['passenger_count'].fillna(median_pax)
        logger_py.info(f"passenger_count null diisi median: {median_pax}")

        # AMBIL DATA BERSIH
        kondisi_hapus = (
            (df['passenger_count'] > 0) &
            (df['fare_amount'].between(LOWER_FARE_GREEN, UPPER_FARE_GREEN)) &
            (df['total_amount'].between(LOWER_TOTAL_AMOUNT_GREEN, UPPER_TOTAL_AMOUNT_GREEN)) &
            (df['tip_amount'].between(LOWER_TIP_AMOUNT_GREEN, UPPER_TIP_AMOUNT_GREEN)) &
            (df['trip_distance'].between(LOWER_TRIP_DISTANCE_GREEN, UPPER_TRIP_DISTANCE_GREEN)) &
            (df['trip_duration_min'].between(LOWER_TRIP_DURATION_MIN_GREEN, UPPER_TRIP_DURATION_MIN_GREEN))
        )
        df_clean = df[kondisi_hapus].copy()
        df_list[i] = df_clean
        logger_py.info(f"Setelah hapus anomali: {df_clean.shape[0]:,} baris")
        logger_py.info(f"Dihapus: {df.shape[0] - df_clean.shape[0]:,} baris")

# CLEAN ALL TAXI
@task(name='Cleaning Yellow and Green Taxi', retries=3, retry_delay_seconds=10)
def clean_taxi(yellow_df_list: list, green_df_list: list):
    logger = get_run_logger()
    logger.info('Start cleaning taxi data')
    cleaning_yellow_taxi(yellow_df_list)
    cleaning_green_taxi(green_df_list)
    logger.info('Finish cleaning taxi data')


def concat_data(df_list: list):
    return pd.concat(df_list, ignore_index=True)

# Save clean data to database
def save_taxi(yellow_df_list: list, green_df_list: list):
    yellow_taxi = concat_data(yellow_df_list)
    green_taxi = concat_data(green_df_list)

    # load cleaned data ke skema silver
    os.makedirs(f'{BASE_DIR}data/silver', exist_ok=True)
    # yellow_taxi.to_parquet(f'{BASE_DIR}data/silver/yellow_trips', index=False)
    # green_taxi.to_parquet(f'{BASE_DIR}data/silver/green_trips', index=False)

    execute_query("CREATE SCHEMA IF NOT EXISTS silver")
    save_to_db(yellow_taxi, 'yellow_trips', 'silver')
    save_to_db(green_taxi, 'green_trips', 'silver')


def preprocess_all_data():
    logger_py.info('Start preprocess all data')
    yellow_df_list = df_yellow_taxi_data()
    green_df_list = df_green_taxi_data()

    drop_unused_columns(yellow_df_list, green_df_list, DROP_COLUMNS_YELLOW, DROP_COLUMNS_GREEN)
    add_trip_duration_min_to_all(yellow_df_list, green_df_list)

    clean_taxi(yellow_df_list, green_df_list)
    logger_py.info('Finish preprocess all data')
    logger_py.info('Save data to duckdb')
    save_taxi(yellow_df_list, green_df_list)
    logger_py.info('Finish save data to duckdb')

def main():
    preprocess_all_data()


if __name__ == '__main__':
    main()