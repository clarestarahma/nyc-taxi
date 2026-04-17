import streamlit as st
import duckdb
from pathlib import Path
from nyc_taxi.utils.db_utils import query_to_df
from nyc_taxi.queries.taxi_queries import TaxiQueries
from nyc_taxi.config.settings import DATA_DIR

st.set_page_config(page_title="NYC Taxi Data Inspector", layout="wide")

st.title("🚖 NYC Taxi - Silver Data Inspector")

def get_data(*, table_name, schema):
    target_table = f"{schema}.{table_name}"
    query = TaxiQueries.GET_ALL_DATA.format(target_table=target_table)
    try:
        return query_to_df(query=query)
    except Exception:
        fallback_path = Path(DATA_DIR) / "silver" / table_name
        if fallback_path.exists():
            return duckdb.connect().execute(
                f"SELECT * FROM read_parquet('{fallback_path.as_posix()}')"
            ).df()
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

    df = get_data(table_name=table, schema=schema)
    
    # Tampilkan Statistik Sederhana
    col1, col2 = st.columns(2)
    col1.metric("Sample Rows", len(df))
    col2.metric("Total Columns", len(df.columns))
    
    # Tampilkan Tabel Interaktif
    st.dataframe(df, width="stretch")
    
    # Tampilkan Info Kolom
    if st.checkbox("Lihat Tipe Data Kolom"):
        st.write(df.dtypes)