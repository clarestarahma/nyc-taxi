import streamlit as st
from nyc_taxi.utils.db_utils import query_to_df
from nyc_taxi.queries.taxi_queries import TaxiQueries

st.set_page_config(page_title="NYC Taxi Data Inspector", layout="wide")

st.title("🚖 NYC Taxi - Raw Data Inspector")

def get_data(*, table_name, schema):
    target_table = f"{schema}.{table_name}"
    query = TaxiQueries.GET_ALL_DATA.format(target_table=target_table)
    df = query_to_df(query=query)
    return df

# Sidebar untuk pilih tabel
table = st.sidebar.selectbox(
    "Pilih Tabel Mentah:",
    ["yellow_taxi", "green_taxi", "weather"]
)

if table:
    st.subheader(f"Data {table.replace('_', ' ').title()}")
    if table == "weather":
        schema = "raw"
    else:
        schema = "raw_taxi"

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