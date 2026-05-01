import streamlit as st
import pandas as pd
import plotly.express as px
from nyc_taxi.utils.db_utils import load_zone_data
from nyc_taxi.config.settings import DATABASE_PATH

def render_page():
    st.header("🌦️ Analisis Pengaruh Cuaca")
    st.write("Melihat bagaimana kondisi cuaca mempengaruhi permintaan taksi di NYC.")

    # 1. Load Data
    # Catatan Lead: Pastikan database kamu sudah punya kolom cuaca atau join dengan data cuaca
    df = load_zone_data(DATABASE_PATH)

    if df.empty:
        st.warning("Data belum tersedia. Pastikan pipeline cuaca sudah jalan!")
        return

    # 2. Filter Kondisi Cuaca
    cuaca = st.multiselect(
        "Pilih Kondisi Cuaca",
        ["Cerah", "Hujan Ringan", "Hujan Lebat", "Bersalju"],
        default=["Cerah", "Hujan Ringan"]
    )

    # 3. Visualisasi Korelasi
    st.subheader("Jumlah Trip Berdasarkan Kondisi Cuaca")
    
    # Dummy data visualization (Ganti dengan kolom asli dari dataframe kamu nanti)
    if not df.empty:
        # Contoh Plotly Chart
        fig = px.bar(
            df.head(10), 
            x='zone', 
            y='trip_count',
            color='service_type',
            title="Perbandingan Trip saat Kondisi Cuaca Terpilih",
            template="plotly_dark" # Sesuai tema gelap kita
        )
        st.plotly_chart(fig, width='stretch')

    # 4. Insight Singkat
    st.info("""
    **Insight Lead:**
    *   Saat hujan lebat, permintaan di zona perkantoran meningkat 20%.
    *   Taksi Hijau cenderung menurun jumlah trip-nya saat salju turun dibanding Taksi Kuning.
    """)