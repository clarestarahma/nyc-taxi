import streamlit as st

def render_page():
    st.header("🔮 Prediksi Jumlah Trip")
    st.write("Masukkan parameter untuk memprediksi permintaan taksi.")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            zone = st.selectbox("Pilih Zona", ["JFK Airport", "Lower Manhattan", "Times Sq"])
            hour = st.slider("Jam (0-23)", 0, 23, 12)
        with col2:
            day = st.selectbox("Hari", ["Monday", "Wednesday", "Friday", "Sunday"])
            is_holiday = st.checkbox("Hari Libur?")
        
        submitted = st.form_submit_button("Prediksi Sekarang")

    if submitted:
        # Tempatkan logika model ML kamu di sini nanti
        st.success(f"Hasil Prediksi: Estimasi 150 trip untuk {zone} pada jam {hour}.")