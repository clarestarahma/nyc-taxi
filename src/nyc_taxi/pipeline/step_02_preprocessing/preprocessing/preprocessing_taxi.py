from nyc_taxi.config.settings import *
from .taxi.ingestion import load_bronze_data
from .taxi.cleaning_taxi_data import clean_taxi, add_trip_duration_min_to_all
from .taxi.drop_unused_columns import drop_unused_columns
from.taxi.enrichment import enrich_taxi_data_zone, enrich_weather_data, clean_after_enrichment
from .taxi.save_data import save_to_silver
from nyc_taxi.config.settings import BRONZE_DIR, PATH_WEATHER_RAW

from prefect import task
import pandas as pd
import logging
import json

logger_py = logging.getLogger("nyc_taxi")
logger_py.setLevel(logging.INFO)


def preprocess_all_data():
    logger_py.info('Start preprocess all data')
    yellow_df_list = load_bronze_data("yellow", BRONZE_DIR)
    green_df_list = load_bronze_data("green", BRONZE_DIR)
    with open(PATH_WEATHER_RAW, 'r') as f:
        weather_json = json.load(f)

    # Drop unused columns
    drop_unused_columns(yellow_df_list, green_df_list, DROP_COLUMNS_YELLOW, DROP_COLUMNS_GREEN)
    add_trip_duration_min_to_all(yellow_df_list, green_df_list)
    clean_taxi(yellow_df_list, green_df_list)

    # Enrichment Zona
    enrich_taxi_data_zone(yellow_df_list, taxi_type="yellow")
    enrich_taxi_data_zone(green_df_list, taxi_type="green")

    # Enrichment Weather
    enrich_weather_data(yellow_df_list, weather_json)
    enrich_weather_data(green_df_list, weather_json)

    # Cleaning after Enrichment
    clean_after_enrichment(yellow_df_list)
    clean_after_enrichment(green_df_list)

    logger_py.info('Finish preprocess all data')
    logger_py.info('Save data to duckdb')
    save_to_silver(yellow_df_list, green_df_list)
    logger_py.info('Finish save data to duckdb')

def main():
    preprocess_all_data()

if __name__ == '__main__':
    main()