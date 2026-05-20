import streamlit as st
import pandas as pd
import plotly.express as px

from nyc_taxi.utils.db_utils import query_to_df


@st.cache_data
def load_weather_analysis_data(taxi_type: str, sample_size: int = 100000) -> pd.DataFrame:
    """
    Load data analisis cuaca dari silver layer.
    Menggunakan sample agar dashboard tetap ringan.
    """

    selected_columns = """
        pickup_hour,
        day_name,
        trip_duration_min,
        total_amount,
        precip_category,
        temp_category
    """

    if taxi_type == "Yellow Taxi":
        query = f"""
        SELECT
            'Yellow Taxi' AS service_type,
            {selected_columns}
        FROM silver.yellow_trips
        USING SAMPLE {sample_size} ROWS
        """

    elif taxi_type == "Green Taxi":
        query = f"""
        SELECT
            'Green Taxi' AS service_type,
            {selected_columns}
        FROM silver.green_trips
        USING SAMPLE {sample_size} ROWS
        """

    else:
        query = f"""
        SELECT
            'Yellow Taxi' AS service_type,
            {selected_columns}
        FROM silver.yellow_trips
        USING SAMPLE {sample_size} ROWS

        UNION ALL

        SELECT
            'Green Taxi' AS service_type,
            {selected_columns}
        FROM silver.green_trips
        USING SAMPLE {sample_size} ROWS
        """

    return query_to_df(query)


def render_page():
    st.header("🌦️ Analisis Pengaruh Cuaca")
    st.write(
        """
        Halaman ini menganalisis hubungan antara kondisi cuaca, suhu, waktu pickup,
        jumlah trip, revenue, dan durasi perjalanan pada data NYC Taxi.
        """
    )

    # =========================
    # FILTER UTAMA
    # =========================
    with st.sidebar:
        st.subheader("🔎 Filter Data")

        col_filter_1, col_filter_2, col_filter_3 = st.columns(3)

        # with col_filter_1:
        taxi_type = st.selectbox(
            "Pilih Jenis Taksi",
            ["Semua Taxi", "Yellow Taxi", "Green Taxi"]
        )

        df = load_weather_analysis_data(taxi_type)

        if df.empty:
            st.warning("Data belum tersedia. Pastikan pipeline preprocessing sudah berjalan.")
            return

        # with col_filter_2:
        precip_options = sorted(df["precip_category"].dropna().unique().tolist())
        selected_precip = st.multiselect(
            "Kategori Curah Hujan",
            precip_options,
            default=precip_options
        )

        # with col_filter_3:
        temp_options = sorted(df["temp_category"].dropna().unique().tolist())
        selected_temp = st.multiselect(
            "Kategori Suhu",
            temp_options,
            default=temp_options
        )

    filtered_df = df[
        df["precip_category"].isin(selected_precip)
        & df["temp_category"].isin(selected_temp)
    ]

    if filtered_df.empty:
        st.warning("Tidak ada data untuk kombinasi filter yang dipilih.")
        return

    # =========================
    # KPI CARDS
    # =========================
    total_trip = len(filtered_df)
    avg_duration = filtered_df["trip_duration_min"].mean()
    avg_revenue = filtered_df["total_amount"].mean()

    dominant_precip = (
        filtered_df["precip_category"].mode().iloc[0]
        if not filtered_df["precip_category"].mode().empty
        else "-"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Trip", f"{total_trip:,}")
    col2.metric("Avg Durasi", f"{avg_duration:.2f} menit")
    col3.metric("Avg Revenue", f"${avg_revenue:.2f}")
    col4.metric("Cuaca Dominan", dominant_precip)

    st.divider()

    col_left_1, col_right_1 = st.columns([1,1])

    # =========================
    # 1. TRIP COUNT PER HOUR
    # =========================
    with col_left_1:
        st.subheader("🚕 Jumlah Trip Berdasarkan Jam Pickup")

        trip_per_hour = (
            filtered_df.groupby("pickup_hour")
            .size()
            .reset_index(name="trip_count")
            .sort_values("pickup_hour")
        )

        fig_hour = px.line(
            trip_per_hour,
            x="pickup_hour",
            y="trip_count",
            markers=True,
            title="Pola Jumlah Trip per Jam",
            labels={
                "pickup_hour": "Jam Pickup",
                "trip_count": "Jumlah Trip"
            },
            template="plotly_dark"
        )

        fig_hour.update_traces(
            line_color='#00d4ff', 
            fill='tozeroy', 
            fillcolor='rgba(0, 212, 255, 0.2)'
        )

        st.plotly_chart(fig_hour, width="stretch")

    # =========================
    # 2. TRIP COUNT BY PRECIP CATEGORY
    # =========================
    with col_right_1:
        st.subheader("🌧️ Jumlah Trip Berdasarkan Kategori Curah Hujan")

        precip_trip = (
            filtered_df.groupby("precip_category")
            .size()
            .reset_index(name="trip_count")
            .sort_values("trip_count", ascending=False)
        )

        fig_precip_trip = px.bar(
            precip_trip,
            x="precip_category",
            y="trip_count",
            color="trip_count",
            color_continuous_scale="YlOrRd",
            text="trip_count",
            title="Jumlah Trip pada Setiap Kategori Curah Hujan",
            labels={
                "precip_category": "Kategori Curah Hujan",
                "trip_count": "Jumlah Trip"
            },
            
            template="plotly_dark"
        )

        fig_precip_trip.update_layout(showlegend=False)

        st.plotly_chart(fig_precip_trip, width="stretch")

    
    col_left_2, col_right_2 = st.columns([1,1])

    # =========================
    # 3. AVG DURATION BY PRECIP CATEGORY
    # =========================
    with col_left_2:
        st.subheader("⏱️ Rata-rata Durasi Perjalanan Berdasarkan Curah Hujan")

        precip_duration = (
            filtered_df.groupby("precip_category")["trip_duration_min"]
            .mean()
            .reset_index(name="avg_duration")
            .sort_values("avg_duration", ascending=False)
        )

        fig_precip_duration = px.bar(
            precip_duration,
            x="precip_category",
            y="avg_duration",
            text_auto=".2f",
            title="Rata-rata Durasi Trip pada Setiap Kategori Curah Hujan",
            color="avg_duration",
            color_continuous_scale="Blues",
            labels={
                "precip_category": "Kategori Curah Hujan",
                "avg_duration": "Rata-rata Durasi (menit)"
            },
            template="plotly_dark"
        )

        fig_precip_duration.update_layout(showlegend=False)

        st.plotly_chart(fig_precip_duration, width="stretch")

    # =========================
    # 4. TRIP COUNT BY TEMP CATEGORY
    # =========================
    with col_right_2:
        st.subheader("🌡️ Jumlah Trip Berdasarkan Kategori Suhu")

        temp_trip = (
            filtered_df.groupby("temp_category")
            .size()
            .reset_index(name="trip_count")
            .sort_values("trip_count", ascending=False)
        )

        fig_temp_trip = px.bar(
            temp_trip,
            x="temp_category",
            y="trip_count",
            text="trip_count",
            title="Jumlah Trip pada Setiap Kategori Suhu",
            color="trip_count",
            color_continuous_scale="YlOrRd",
            labels={
                "temp_category": "Kategori Suhu",
                "trip_count": "Jumlah Trip"
            },
            template="plotly_dark"
        )

        fig_temp_trip.update_layout(showlegend=False)

        st.plotly_chart(fig_temp_trip, width="stretch")

    # =========================
    # INSIGHT
    # =========================
    st.subheader("📌 Insight Analisis")

    peak_hour = trip_per_hour.loc[trip_per_hour["trip_count"].idxmax(), "pickup_hour"]
    peak_hour_trip = trip_per_hour["trip_count"].max()

    highest_precip = precip_trip.iloc[0]["precip_category"]
    highest_precip_trip = precip_trip.iloc[0]["trip_count"]

    highest_duration_precip = precip_duration.iloc[0]["precip_category"]
    highest_duration_value = precip_duration.iloc[0]["avg_duration"]

    st.info(
        f"""
        **Ringkasan Insight:**

        - Jumlah trip tertinggi terjadi pada jam **{peak_hour}:00** dengan sekitar **{peak_hour_trip:,} trip** pada data sample.
        - Kategori curah hujan dengan jumlah trip terbanyak adalah **{highest_precip}** dengan sekitar **{highest_precip_trip:,} trip**.
        - Rata-rata durasi perjalanan tertinggi terjadi pada kategori **{highest_duration_precip}**, yaitu sekitar **{highest_duration_value:.2f} menit**.
        - Filter jenis taksi, kategori curah hujan, dan kategori suhu membantu melihat perubahan pola permintaan taxi pada kondisi cuaca yang berbeda.
        """
    )