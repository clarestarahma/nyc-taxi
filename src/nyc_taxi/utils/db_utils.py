import duckdb
import pandas as pd
from nyc_taxi.config.settings import DATA_DIR, DATABASE_PATH, NYC_TAXI_DIR
import os
import logging
import streamlit as st
import pandas as pd
import json
import duckdb
from pathlib import Path

from nyc_taxi.queries.taxi_queries import TaxiQueries


# def get_connection():
#     if not os.path.exists(DATA_DIR):
#         os.makedirs(DATA_DIR)
#         print("📁 Folder 'data' berhasil dibuat otomatis!")
        
#     return duckdb.connect(DATABASE_PATH)

def get_connection():
    token = st.secrets.get("MOTHERDUCK_TOKEN")
    
    if token:
        return duckdb.connect(f"md:nyc_taxi_cloud?motherduck_token={token}")
    
    else:
        # TEMA LOKAL (Laptop Kamu): Konek ke file .db lokal seperti biasa
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print("📁 Folder 'data' berhasil dibuat otomatis!")
            
        return duckdb.connect(DATABASE_PATH)

def save_to_db(df: pd.DataFrame, table_name: str, schema: str):
    """
    Simpan dataframe ke DuckDB pada schema dan table tertentu.
    Menggunakan CREATE OR REPLACE agar tabel silver/gold diperbarui setiap pipeline dijalankan.
    """
    logger = logging.getLogger(__name__)
    target_table = f"{schema}.{table_name}"

    try:
        with get_connection() as conn:
            # Pastikan schema tersedia
            conn.execute(
                TaxiQueries.CREATE_SCHEMA.format(schema_name=schema)
            )

            # Register dataframe agar bisa dibaca DuckDB
            conn.register("df", df)

            # Simpan dataframe ke tabel DuckDB
            conn.execute(f"""
                CREATE OR REPLACE TABLE {target_table} AS
                SELECT * FROM df
            """)

        logger.info(f"✅ [DB] {target_table} berhasil disimpan.")

    except Exception as e:
        logger.error(f"❌ [DB] Gagal simpan ke DuckDB ({target_table}): {e}")
        raise

def query_to_df(query: str) -> pd.DataFrame:
    """Function for run SELECT and returning Pandas DataFrame"""
    with get_connection() as conn:
        return conn.execute(query).df()
    
def execute_query(query: str, conn=None):
    if conn is None:
        with get_connection() as c:
            c.execute(query)
    else:
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