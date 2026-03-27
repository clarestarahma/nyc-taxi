import streamlit as st
import duckdb
import pandas as pd
from nyc_taxi.utils.duckdb import execute_query, query_to_df, get_connection

st.set_page_config(page_title="NYC Taxi Data Inspector", layout="wide")

st.title("🚖 NYC Taxi - Raw Data Inspector")

def get_data(table_name):
    with duckdb.connect("data/nyc_taxi.db", read_only=True) as conn:
        query = f"SELECT * FROM raw.{table_name} LIMIT 1000"
        df = conn.execute(query).df()
    return df

# Sidebar untuk pilih tabel
table = st.sidebar.selectbox(
    "Pilih Tabel Mentah:",
    ["yellow_taxi", "green_taxi", "fhv_taxi", "hvfhv_taxi"]
)

if table:
    st.subheader(f"Data {table.replace('_', ' ').title()}")
    df = get_data(table)
    
    # Tampilkan Statistik Sederhana
    col1, col2 = st.columns(2)
    col1.metric("Sample Rows", len(df))
    col2.metric("Total Columns", len(df.columns))
    
    # Tampilkan Tabel Interaktif
    st.dataframe(df, width="stretch")
    
    # Tampilkan Info Kolom
    if st.checkbox("Lihat Tipe Data Kolom"):
        st.write(df.dtypes)