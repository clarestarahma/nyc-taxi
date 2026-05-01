import streamlit as st
from nyc_taxi.config.settings import DATABASE_PATH

from nyc_taxi.pipeline.step_05_dashboard.pages import zona_revenue, pengaruh_cuaca, prediksi_trip

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
        page_title="NYC Taxi Dashboard",
        page_icon="🚕",
        layout="wide",
    )

# --- SIDEBAR NAVIGASI (MANUAL) ---
with st.sidebar:
    st.title("🚕 NYC Taxi")
    st.write("Dashboard Analisis Data")
    
    # Inilah yang menggantikan navigasi otomatis tadi
    selected_page = st.selectbox(
        "Pilih Halaman",
        ["Zona Revenue", "Pengaruh Cuaca", "Prediksi Trip"]
    )

# --- LOGIKA RENDER HALAMAN (CONTROLLER) ---
# Di sini kita panggil fungsi render dari masing-masing file di folder pages
if "Zona Revenue" in selected_page:
    zona_revenue.render_page()
elif "Pengaruh Cuaca" in selected_page:
    pengaruh_cuaca.render_page()
elif "Prediksi Trip" in selected_page:
    prediksi_trip.render_page()