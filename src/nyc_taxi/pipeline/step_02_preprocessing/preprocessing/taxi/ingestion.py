import pandas as pd
from prefect import task
import pandas as pd

@task(name="Load Bronze Data", retries=3, retry_delay_seconds=10)
def load_bronze_data(color, bronze_dir):
    files = sorted(list(bronze_dir.glob(f"{color}_tripdata_2025-*.parquet")))
    
    return [pd.read_parquet(f) for f in files]