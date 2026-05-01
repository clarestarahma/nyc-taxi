from nyc_taxi.config.settings import ROOT_DIR
from nyc_taxi.utils.db_utils import execute_query, save_to_db

import pandas as pd
import os

def concat_data(df_list: list):
    return pd.concat(df_list, ignore_index=True)

# Save clean data to database
def save_to_silver(yellow_df_list: list, green_df_list: list):
    yellow_taxi = concat_data(yellow_df_list)
    green_taxi = concat_data(green_df_list)

    # load cleaned data ke skema silver
    os.makedirs(f'{ROOT_DIR}data/silver', exist_ok=True)
    # yellow_taxi.to_parquet(f'{BASE_DIR}data/silver/yellow_trips', index=False)
    # green_taxi.to_parquet(f'{BASE_DIR}data/silver/green_trips', index=False)

    execute_query("CREATE SCHEMA IF NOT EXISTS silver")
    save_to_db(yellow_taxi, 'yellow_trips', 'silver')
    save_to_db(green_taxi, 'green_trips', 'silver')