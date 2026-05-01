import duckdb
import pandas as pd
from nyc_taxi.config.settings import DATA_DIR, DATABASE_PATH, NYC_TAXI_DIR
import os
import logging
import streamlit as st
import pandas as pd
import json
import duckdb
import pugsql
from pathlib import Path

from nyc_taxi.queries.taxi_queries import TaxiQueries


def get_connection():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print("📁 Folder 'data' berhasil dibuat otomatis!")
        
    return duckdb.connect(DATABASE_PATH)

def save_to_db(df: pd.DataFrame, table_name: str, schema: str):
    logger = logging.getLogger(__name__)
    target_table = f"{schema}.{table_name}"
    try:
        # 1. Pastikan Schema & Tabel ada (Auto-commit DDL)
        query = TaxiQueries.CREATE_SCHEMA.format(schema_name=schema)
        execute_query(query=query)

        # Buat tabel kosong jika belum ada
        query = TaxiQueries.CREATE_TABLE.format(target_table=target_table)
        query_to_df(query=query, df=df)
        
        logger.info(f"📥 [DB] Menambahkan {len(df)} baris ke {target_table}...")
        
        # 3. Gunakan INSERT INTO daripada append untuk kestabilan antar schema
        # DuckDB bisa langsung baca DataFrame 'df' di dalam query SQL
        query = TaxiQueries.INSERT.format(target_table=target_table)
        query_to_df(query=query, df=df)
        
        logger.info(f"✅ [DB] {table_name} updated successfully.")
        
    except Exception as e:
        logger.error(f"❌ [DB] Gagal simpan ke DuckDB ({target_table}): {e}")

def execute_query(*, query: str, df: pd.DataFrame):
    """General function for run SQL query without returning data"""
    try:
        with get_connection() as conn:
            if df is not None:
                conn.register("df", df)
            
            conn.execute(query)
    except KeyboardInterrupt:
        print('Interupsi. Program dihentikan')
        raise

def query_to_df(query: str) -> pd.DataFrame:
    """Function for run SELECT and returning Pandas DataFrame"""
    with get_connection() as conn:
        return conn.execute(query).df()
    
def execute_query(query: str):
    """Function for run SELECT and returning Pandas DataFrame"""
    with get_connection() as conn:
        conn.execute(query)

# =========================
# HELPERS
# =========================
@st.cache_data
def load_zone_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    sql_file = NYC_TAXI_DIR / "queries" / "silver_to_gold_profitability.sql"

    if not sql_file.exists():
        st.error(f"File SQL tidak ditemukan di: {sql_file}")
        return pd.DataFrame()
    
    query = sql_file.read_text().strip()

    # print(query)

    try:
        # 3. Koneksi ke DuckDB dan ambil data
        df = query_to_df(query)
        
        # 4. Standardisasi: Kecilkan semua nama kolom (mencegah KeyError)
        df.columns = [col.lower() for col in df.columns]
        
        # 5. Pastikan kolom angka benar-benar tipe numerik
        numeric_cols = ["trip_count", "total_revenue", "avg_fare", "avg_tip"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        numeric_cols = ["trip_count", "total_revenue", "avg_fare", "avg_tip", "pickup_location_id"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in ["zone", "borough", "service_type"]:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown")

        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari database: {e}")
        return pd.DataFrame()
    


@st.cache_data
def load_geojson(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def weighted_average(df: pd.DataFrame, value_col: str, weight_col: str = "trip_count") -> float:
    if df.empty or df[weight_col].sum() == 0:
        return 0.0
    return (df[value_col] * df[weight_col]).sum() / df[weight_col].sum()