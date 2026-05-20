import streamlit as st
import altair as alt
from nyc_taxi.utils.db_utils import load_zone_data, load_geojson
from nyc_taxi.utils.dashboard_utils import METRIC_LABELS
from nyc_taxi.config.settings import DATABASE_PATH, PATH_GEOJSON

from ..components.maps import render_nyc_map
from ..components.cards import render_metric_cards
from ..components.top_zones_charts import render_top_zones_chart
from ..components.borough_analysis import render_borough_analysis

def render_page():
    st.title("💰 Zona Operasi Paling Menguntungkan")
    st.subheader("Optimasi Pendapatan Berdasarkan Lokasi")
    st.info("💡 **Tips:** Perhatikan perbedaan antara **Total Revenue** (Volume) dan **Average Fare** (Kualitas). Zona dengan trip sedikit bisa jadi punya rata-rata tarif yang sangat tinggi!")

    # =========================
    # LOAD DATA 
    # =========================
    df = load_zone_data()
    
    try:
        geo_data = load_geojson(PATH_GEOJSON)
    except Exception as e:
        st.error(f"GeoJSON file not found: {e}")
        return # Berhenti jika geojson tidak ada

    if df.empty:
        st.warning("Data at database is empty")
        return


    # =========================
    # FILTER DI SIDEBAR
    # =========================
    with st.sidebar:
        st.header("Filter Eksplorasi")
        
        # Filter Borough (Manhattan, Brooklyn, dll)
        all_boroughs = sorted(df['borough'].unique())
        selected_boroughs = st.multiselect("Pilih Borough", all_boroughs, default=all_boroughs)
        
        # Filter Service Type (Yellow/Green)
        all_services = sorted(df['service_type'].unique())
        selected_services = st.multiselect("Tipe Layanan", all_services, default=all_services)

        st.header("Konfigurasi Visual")
        top_n = st.slider(
        "Tampilkan Top Berapa Data?", 
        min_value=3, 
        max_value=7, 
        value=5, 
        step=1,
        help="Geser untuk mengatur jumlah Borough atau Zona yang ditampilkan di semua grafik."
    )

    # =========================
    # PROSES FILTERING
    # =========================
    df_filtered = df[
        (df['borough'].isin(selected_boroughs)) & 
        (df['service_type'].isin(selected_services))
    ]

    # =========================
    # CARD
    # =========================
    render_metric_cards(df_filtered)


    # =========================
    # METRIC SELECTION
    # =========================
    metric = st.selectbox("Pilih Metrik", list(
        METRIC_LABELS.keys()), format_func=lambda x: METRIC_LABELS[x])
    
    # st.divider()
    
    # =========================
    # MAP & SIDE VISUALIZATION
    # =========================

    col_left, col_right = st.columns([2, 1]) 

    with col_left:
        st.subheader(f"Sebaran {METRIC_LABELS[metric]}")
        # Render peta di sini (pindahkan dari baris sebelumnya) <--- DIPINDAH
        render_nyc_map(geo_data, df_filtered, metric)

    with col_right:
        render_borough_analysis(df_filtered, metric, METRIC_LABELS[metric], top_n)

    # =========================
    # ADDITIONAL ANALYSIS
    # =========================
    st.divider()
    
    col_1, col_2 = st.columns([2, 1])

    with col_1:
        # Panggil komponen Top 10 Chart
        render_top_zones_chart(df_filtered, metric, METRIC_LABELS[metric], top_n)

    with col_2:
        st.write("### 📋 Detail Data")
        # Tampilkan tabel data agar user bisa copy-paste angka jika perlu
        st.dataframe(
            df_filtered[['zone', 'borough', metric]]
            .sort_values(by=metric, ascending=False)
            .head(top_n),
            hide_index=True,
            width='stretch'
        )

    # Menaruh checkbox sampel data di paling bawah
    if st.checkbox("Lihat Sampel Data"):
        st.write(df_filtered[['pickup_location_id', 'zone', metric]].head())