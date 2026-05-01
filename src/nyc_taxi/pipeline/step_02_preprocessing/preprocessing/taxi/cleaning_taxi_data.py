# step_2_preprocessing/cleaning.py
from prefect import task
from prefect.logging import get_run_logger
import logging

# Import threshold dari config kamu
from nyc_taxi.config.settings import *

# CLEANING YELLOW
def cleaning_yellow_taxi(df_list: list):
    logger_py = logging.getLogger()
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
    logger_py = logging.getLogger()
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