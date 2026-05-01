from prefect import task
from nyc_taxi.utils.db_utils import save_to_db

@task
def load_zone_profitability(df):
    save_to_db(df, "zone_profitability", "gold")