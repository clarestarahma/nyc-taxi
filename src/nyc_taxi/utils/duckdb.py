import duckdb
import pandas as pd
from nyc_taxi.config import settings
import os
import logging

def get_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
        print("📁 Folder 'data' berhasil dibuat otomatis!")
        
    return duckdb.connect(settings.RAW_DB_PATH)

def save_to_raw(df: pd.DataFrame, table_name: str):
    logger = logging.getLogger(__name__)
    try:
        # 1. Pastikan Schema & Tabel ada (Auto-commit DDL)
        execute_query("CREATE SCHEMA IF NOT EXISTS raw")
        
        target_table = f"raw.{table_name}"
        
        # Buat tabel kosong jika belum ada
        execute_query(f"CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM df WHERE 1=0")
        
        logger.info(f"📥 [DB] Menambahkan {len(df)} baris ke {target_table}...")
        
        # 2. Gunakan INSERT INTO daripada append untuk kestabilan antar schema
        # DuckDB bisa langsung baca DataFrame 'df' di dalam query SQL
        execute_query(f"INSERT INTO {target_table} SELECT * FROM df")
        
        logger.info(f"✅ [DB] {table_name} updated successfully.")
        
    except Exception as e:
        logger.error(f"❌ [DB] Gagal simpan ke DuckDB: {e}")

def execute_query(query: str):
    """General function for run SQL query without returning data"""
    with get_connection as conn:
        conn.execute(query)

def query_to_df(query: str) -> pd.DataFrame:
    """Function for run SELECT and returning Pandas DataFrame"""
    with get_connection() as conn:
        return conn.execute(query).df()