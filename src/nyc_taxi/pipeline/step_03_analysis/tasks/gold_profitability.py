from prefect import task, get_run_logger
import duckdb
from nyc_taxi.config.settings import DATABASE_PATH, NYC_TAXI_DIR
from nyc_taxi.utils.db_utils  import get_connection

@task
def fetch_zone_profitability():
    logger = get_run_logger()

    sql = (NYC_TAXI_DIR / "queries" / "silver_to_gold_profitability.sql").read_text()

    with get_connection() as con:
        df = con.execute(sql).df()

    logger.info(f"Fetched {len(df)} rows from DuckDB")
    return df