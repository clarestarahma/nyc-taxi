from nyc_taxi.pipeline.step_01_ingestion.taxi import ingest_all_taxi_parquet
from nyc_taxi.pipeline.step_01_ingestion.weather import ingest_weather_data

from prefect import flow

@flow(name = "Ingest Taxi and Weather Data")
def ingest_data():
    try:
        ingest_all_taxi_parquet()
        ingest_weather_data()
    except KeyboardInterrupt:
        print("\n🛑 Program dihentikan paksa oleh user (KeyboardInterrupt)")
        return

if __name__ == "__main__":
    ingest_data()