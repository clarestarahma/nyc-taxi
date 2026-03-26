import duckdb
import pandas as pd
from nyc_taxi.config import settings
import os

def get_connection():
    if not os.path.exists("data"):
        os.makedirs("data")
        print("📁 Folder 'data' berhasil dibuat otomatis!")
        
    return duckdb.connect(settings.RAW_DB_PATH)

def save_to_raw(df: pd.DataFrame, table_name: str):
    with get_connection() as conn:
        try:
            # 1. Pastikan Schema & Tabel ada (Auto-commit DDL)
            conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
            
            target_table = f"raw.{table_name}"
            
            # Buat tabel kosong jika belum ada
            conn.execute(f"CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM df WHERE 1=0")
            
            print(f"📥 [DB] Menambahkan {len(df)} baris ke {target_table}...")
            
            # 2. Gunakan INSERT INTO daripada append untuk kestabilan antar schema
            # DuckDB bisa langsung baca DataFrame 'df' di dalam query SQL
            conn.execute(f"INSERT INTO {target_table} SELECT * FROM df")
            
            print(f"✅ [DB] {table_name} updated successfully.")
            
        except Exception as e:
            print(f"❌ [DB] Gagal simpan ke DuckDB: {e}")