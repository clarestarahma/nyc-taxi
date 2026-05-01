from prefect import task, get_run_logger
import duckdb
from nyc_taxi.config.settings import DATABASE_PATH, NYC_TAXI_DIR

@task
def fetch_zone_profitability():
    logger = get_run_logger()

    sql = (NYC_TAXI_DIR / "queries" / "silver_to_gold_profitability.sql").read_text()

    with duckdb.connect(str(DATABASE_PATH), read_only=True) as con:
        df = con.execute(sql).df()

    logger.info(f"Fetched {len(df)} rows from DuckDB")
    return df