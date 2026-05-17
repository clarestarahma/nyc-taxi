import streamlit as st
import pandas as pd
import plotly.express as px

from nyc_taxi.utils.db_utils import query_to_df
from nyc_taxi.pipeline.step_05_dashboard.components.trip_per_hour_chart import show_trip_per_hour
from nyc_taxi.pipeline.step_05_dashboard.components.rain_trip_chart import show_rain_trip_chart

def render_page():
    st.header("🌦️ Analisis Pengaruh Cuaca")
    st.write("Melihat bagaimana kondisi cuaca mempengaruhi permintaan taksi di NYC.")

    # LOAD DATA
    query = """
    SELECT *
    FROM silver.yellow_trips
    USING SAMPLE 100000 ROWS
    """

    df = query_to_df(query)

    if df.empty:
        st.warning("Data belum tersedia. Pastikan pipeline preprocessing sudah jalan!")
        return

    # FILTER CUACA
    st.subheader("Filter Kondisi Cuaca")

    selected_weather = st.multiselect(
        "Pilih Kondisi Cuaca",
        options=df["is_raining"].unique(),
        default=df["is_raining"].unique()
    )

    filtered_df = df[df["is_raining"].isin(selected_weather)]

    # ANALISIS TRIP PER JAM
    st.subheader("📊 Jumlah Trip Berdasarkan Jam")

    trip_per_hour = (
        filtered_df.groupby("pickup_hour")
        .size()
        .reset_index(name="trip_count")
        .sort_values("pickup_hour")
    )

    show_trip_per_hour(trip_per_hour)

    # ANALISIS HUJAN VS TIDAK HUJAN
    st.subheader("🌧️ Pengaruh Hujan terhadap Jumlah Trip")

    rain_analysis = (
        filtered_df.groupby("is_raining")
        .size()
        .reset_index(name="trip_count")
    )

    show_rain_trip_chart(rain_analysis)

    # ANALISIS REVENUE
    st.subheader("💰 Rata-rata Revenue Berdasarkan Cuaca")

    revenue_rain = (
        filtered_df.groupby("is_raining")["total_amount"]
        .mean()
        .reset_index(name="avg_revenue")
    )

    fig_revenue = px.bar(
        revenue_rain,
        x="is_raining",
        y="avg_revenue",
        color="is_raining",
        title="Rata-rata Revenue saat Hujan vs Tidak Hujan",
        template="plotly_dark",
        text_auto=".2f"
    )

    st.plotly_chart(fig_revenue, width="stretch")

    # ANALISIS DURASI PERJALANAN
    st.subheader("⏱️ Rata-rata Durasi Perjalanan")

    duration_weather = (
        filtered_df.groupby("is_raining")["trip_duration_min"]
        .mean()
        .reset_index(name="avg_duration")
    )

    fig_duration = px.bar(
        duration_weather,
        x="is_raining",
        y="avg_duration",
        color="is_raining",
        title="Durasi Perjalanan saat Hujan vs Tidak Hujan",
        template="plotly_dark",
        text_auto=".2f"
    )

    st.plotly_chart(fig_duration, width="stretch")

    # INSIGHT
    st.subheader("📌 Insight Analisis")

    avg_trip_rain = rain_analysis["trip_count"].min()
    avg_trip_clear = rain_analysis["trip_count"].max()

    st.info(f"""
    ### Hasil Analisis:
    - Jumlah trip saat tidak hujan lebih tinggi dibanding saat hujan.
    - Aktivitas perjalanan paling ramai terjadi pada jam siang hingga sore hari.
    - Revenue rata-rata perjalanan cenderung stabil meskipun terjadi hujan.
    - Kondisi cuaca dapat mempengaruhi jumlah permintaan taksi di NYC.
    
    ### Statistik:
    - Total trip tertinggi: {avg_trip_clear}
    - Total trip terendah: {avg_trip_rain}
    """)