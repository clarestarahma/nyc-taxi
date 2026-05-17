import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = Path("models/trip_predictor.pkl")
model = joblib.load(MODEL_PATH)

def render_page():

    st.header("🔮 Prediksi Jumlah Trip")
    st.write("Prediksi jumlah trip taxi berdasarkan waktu dan kondisi cuaca.")

    with st.form("prediction_form"):

        col1, col2 = st.columns(2)

        with col1:
            pickup_hour = st.slider("Jam Pickup", 0, 23, 12)

            day_name = st.selectbox(
                "Hari",
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday"
                ]
            )

        with col2:
            is_raining = st.selectbox(
                "Apakah Sedang Hujan?",
                ["Tidak", "Ya"]
            )

        submitted = st.form_submit_button("Prediksi Sekarang")

    if submitted:

        input_data = {
            "pickup_hour": pickup_hour,
            "is_raining": 1 if is_raining == "Ya" else 0,
            "day_name_Monday": 0,
            "day_name_Saturday": 0,
            "day_name_Sunday": 0,
            "day_name_Thursday": 0,
            "day_name_Tuesday": 0,
            "day_name_Wednesday": 0
        }

        if day_name != "Friday":
            input_data[f"day_name_{day_name}"] = 1

        input_df = pd.DataFrame([input_data])

        prediction = model.predict(input_df)[0]

        st.success(
            f"📈 Estimasi jumlah trip taxi: {int(prediction)} trip"
        )

        if is_raining == "Ya":
            st.info("🌧️ Cuaca hujan dapat mempengaruhi pola permintaan taxi.")
        else:
            st.info("☀️ Cuaca cerah biasanya memiliki pola perjalanan normal.")