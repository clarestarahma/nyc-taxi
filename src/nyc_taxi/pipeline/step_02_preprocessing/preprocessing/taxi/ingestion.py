from pathlib import Path
import pandas as pd
from prefect import task
from prefect.logging import get_run_logger
from pathlib import Path
import pandas as pd

@task(name="Load Bronze Data", retries=3, retry_delay_seconds=10)
def load_bronze_data(color, bronze_dir):
    files = sorted(list(bronze_dir.glob(f"{color}_tripdata_2025-*.parquet")))
    
    # Baca semua file tersebut dan jadikan satu list
    return [pd.read_parquet(f) for f in files]