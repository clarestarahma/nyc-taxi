import streamlit as st
import duckdb
from pathlib import Path
from nyc_taxi.utils.db_utils import query_to_df
from nyc_taxi.queries.taxi_queries import TaxiQueries
from nyc_taxi.config.settings import DATA_DIR

st.set_page_config(page_title="NYC Taxi Data Inspector", layout="wide")

st.title("🚖 NYC Taxi - Silver Data Inspector")

# update fungsi get_data 
def get_data(*, table_name, schema, limit=1000):
    target_table = f"{schema}.{table_name}"

    preview_query = f"""
        SELECT *
        FROM {target_table}
        LIMIT {limit}
    """

    count_query = f"""
        SELECT COUNT(*) AS total_rows
        FROM {target_table}
    """

    try:
        preview_df = query_to_df(query=preview_query)
        total_rows = query_to_df(query=count_query)["total_rows"][0]

        return preview_df, total_rows

    except Exception:
        fallback_path = Path(DATA_DIR) / "silver" / table_name

        if fallback_path.exists():

            preview_df = duckdb.connect().execute(
                f"""
                SELECT *
                FROM read_parquet('{fallback_path.as_posix()}')
                LIMIT {limit}
                """
            ).df()

            total_rows = duckdb.connect().execute(
                f"""
                SELECT COUNT(*) AS total_rows
                FROM read_parquet('{fallback_path.as_posix()}')
                """
            ).fetchone()[0]

            return preview_df, total_rows

        raise

# Sidebar untuk pilih tabel
table = st.sidebar.selectbox(
    "Pilih Tabel Silver:",
    ["yellow_trips", "green_trips", "weather"]
)

if table:
    st.subheader(f"Data {table.replace('_', ' ').title()}")
    schema = "silver"
    if table == "weather":
        st.info("📅 Data cuaca harian untuk NYC, termasuk suhu, curah hujan, kecepatan angin, dll.")
    else:
        st.info("🚕 Data perjalanan taksi NYC, termasuk waktu penjemputan, lokasi, jarak, tarif, dll.")

    df, total_rows = get_data(table_name=table, schema=schema)
    
    # Tampilkan Statistik Sederhana
    col1, col2 = st.columns(2)
    col1.metric("Total Rows", f"{total_rows:,}")
    col2.metric("Total Columns", len(df.columns))
    
    # Tampilkan Tabel Interaktif
    st.dataframe(df, width="stretch")
    
    # Tampilkan Info Kolom
    if st.checkbox("Lihat Tipe Data Kolom"):
        st.write(df.dtypes)