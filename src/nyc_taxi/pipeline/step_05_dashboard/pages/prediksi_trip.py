from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from nyc_taxi.utils.db_utils import query_to_df
from nyc_taxi.config.settings import MODEL_PATH, FEATURES_PATH, METRICS_PATH


# MODEL_PATH = Path("models/trip_predictor.pkl")
# FEATURES_PATH = Path("models/trip_predictor_features.pkl")
# METRICS_PATH = Path("models/trip_predictor_metrics.pkl")


@st.cache_resource
def load_prediction_assets():
    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURES_PATH)
    metrics = joblib.load(METRICS_PATH)

    return model, feature_columns, metrics


@st.cache_data
def load_category_options():
    query = """
    SELECT DISTINCT precip_category, temp_category
    FROM silver.yellow_trips

    UNION

    SELECT DISTINCT precip_category, temp_category
    FROM silver.green_trips
    """

    df = query_to_df(query)

    precip_options = sorted(df["precip_category"].dropna().unique().tolist())
    temp_options = sorted(df["temp_category"].dropna().unique().tolist())

    return precip_options, temp_options


def create_prediction_input(
    service_type: str,
    pickup_hour: int,
    day_name: str,
    precip_category: str,
    temp_category: str,
    feature_columns: list
) -> pd.DataFrame:
    input_df = pd.DataFrame([
        {
            "service_type": service_type,
            "pickup_hour": pickup_hour,
            "day_name": day_name,
            "precip_category": precip_category,
            "temp_category": temp_category,
        }
    ])

    input_encoded = pd.get_dummies(input_df)

    # Samakan kolom input dengan kolom saat training
    input_encoded = input_encoded.reindex(
        columns=feature_columns,
        fill_value=0
    )

    return input_encoded


def predict_trip_count(
    model,
    feature_columns,
    taxi_type,
    pickup_hour,
    day_name,
    precip_category,
    temp_category
):
    if taxi_type == "Semua Taxi":
        yellow_input = create_prediction_input(
            service_type="Yellow Taxi",
            pickup_hour=pickup_hour,
            day_name=day_name,
            precip_category=precip_category,
            temp_category=temp_category,
            feature_columns=feature_columns
        )

        green_input = create_prediction_input(
            service_type="Green Taxi",
            pickup_hour=pickup_hour,
            day_name=day_name,
            precip_category=precip_category,
            temp_category=temp_category,
            feature_columns=feature_columns
        )

        yellow_prediction = model.predict(yellow_input)[0]
        green_prediction = model.predict(green_input)[0]

        return yellow_prediction + green_prediction

    input_data = create_prediction_input(
        service_type=taxi_type,
        pickup_hour=pickup_hour,
        day_name=day_name,
        precip_category=precip_category,
        temp_category=temp_category,
        feature_columns=feature_columns
    )

    return model.predict(input_data)[0]


def render_page():
    st.header("🔮 Prediksi Jumlah Trip")
    st.write(
        """
        Halaman ini memprediksi estimasi jumlah trip taxi berdasarkan jenis taksi,
        waktu pickup, hari, kategori curah hujan, dan kategori suhu.
        """
    )

    if not MODEL_PATH.exists() or not FEATURES_PATH.exists() or not METRICS_PATH.exists():
        st.warning(
            """
            Model prediksi belum tersedia. Pastikan model sudah dilatih dan file berikut tersedia:
            `trip_predictor.pkl`, `trip_predictor_features.pkl`, dan `trip_predictor_metrics.pkl`.
            """
        )
        return

    model, feature_columns, metrics = load_prediction_assets()
    precip_options, temp_options = load_category_options()

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            taxi_type = st.selectbox(
                "Pilih Jenis Taksi",
                ["Semua Taxi", "Yellow Taxi", "Green Taxi"]
            )

            pickup_hour = st.slider(
                "Jam Pickup",
                min_value=0,
                max_value=23,
                value=12
            )

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
            precip_category = st.selectbox(
                "Kategori Curah Hujan",
                precip_options
            )

            temp_category = st.selectbox(
                "Kategori Suhu",
                temp_options
            )

        submitted = st.form_submit_button("Prediksi Sekarang")

    if submitted:
        prediction = predict_trip_count(
            model=model,
            feature_columns=feature_columns,
            taxi_type=taxi_type,
            pickup_hour=pickup_hour,
            day_name=day_name,
            precip_category=precip_category,
            temp_category=temp_category
        )

        prediction = max(0, round(prediction))

        st.divider()

        st.subheader("📈 Hasil Prediksi")

        col_result, col_mae, col_r2 = st.columns(3)

        col_result.metric(
            label="Estimasi Jumlah Trip",
            value=f"{prediction:,} trip"
        )

        col_mae.metric(
            label="MAE Model",
            value=f"{metrics['mae']:.2f}"
        )

        col_r2.metric(
            label="R² Score",
            value=f"{metrics['r2']:.3f}"
        )

        st.info(
            f"""
            Model memperkirakan sekitar **{prediction:,} trip** untuk **{taxi_type}**
            pada hari **{day_name}** pukul **{pickup_hour}:00**, dengan kondisi
            curah hujan **{precip_category}** dan suhu **{temp_category}**.
            """
        )

        st.caption(
            """
            Catatan: Prediksi dibuat berdasarkan pola historis data Yellow Taxi dan Green Taxi selama periode analisis.
            """
        )