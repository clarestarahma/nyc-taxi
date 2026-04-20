from .preprocessing.preprocessing_weather import preprocess_data as weather_preprocess_data
from .preprocessing.preprocessing_taxi import preprocess_all_data as taxi_preprocess_data

from prefect import flow

@flow(name="Preprocessing and saving to duckdb")
def main():
    weather_preprocess_data()
    taxi_preprocess_data()

if __name__ == '__main__':
    main()