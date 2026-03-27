import duckdb
import pandas as pd
from nyc_taxi.config import settings
import os
import logging
from nyc_taxi.queries.taxi_queries import TaxiQueries

def get_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
        print("📁 Folder 'data' berhasil dibuat otomatis!")
        
    return duckdb.connect(settings.RAW_DB_PATH)

def save_to_raw(df: pd.DataFrame, table_name: str, schema: str):
    logger = logging.getLogger(__name__)
    target_table = f"{schema}.{table_name}"
    try:
        # 1. Pastikan Schema & Tabel ada (Auto-commit DDL)
        query = TaxiQueries.CREATE_SCHEMA.format(schema_name=schema)
        execute_query(query=query, df=None)

        # Buat tabel kosong jika belum ada
        query = TaxiQueries.CREATE_TABLE.format(target_table=target_table)
        execute_query(query=query, df=df)
        
        logger.info(f"📥 [DB] Menambahkan {len(df)} baris ke {target_table}...")
        
        # 3. Gunakan INSERT INTO daripada append untuk kestabilan antar schema
        # DuckDB bisa langsung baca DataFrame 'df' di dalam query SQL
        query = TaxiQueries.INGEST_YELLOW_TAXI.format(target_table=target_table)
        execute_query(query=query, df=df)
        
        logger.info(f"✅ [DB] {table_name} updated successfully.")
        
    except Exception as e:
        logger.error(f"❌ [DB] Gagal simpan ke DuckDB ({target_table}): {e}")

def execute_query(*, query: str, df: pd.DataFrame):
    """General function for run SQL query without returning data"""
    with get_connection() as conn:
        if df is not None:
            conn.register("df", df)
        
        conn.execute(query)

def query_to_df(query: str) -> pd.DataFrame:
    """Function for run SELECT and returning Pandas DataFrame"""
    with get_connection() as conn:
        return conn.execute(query).df()