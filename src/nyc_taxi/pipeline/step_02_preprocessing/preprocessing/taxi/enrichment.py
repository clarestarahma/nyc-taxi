from nyc_taxi.config.settings import DATA_DIR

from prefect import task, get_run_logger
import pandas as pd

@task(name='Enrich Taxi Data', retries=3, retry_delay_seconds=10)
def enrich_taxi_data_zone(df_list: list, taxi_type: str):
    logger = get_run_logger()
    logger.info(f'Starting enrichment for {taxi_type} taxi')
    
    # Load lookup table (Master Data)
    lookup = pd.read_csv(f"{DATA_DIR}/static/taxi_zone_lookup.csv")
    
    for i, df in enumerate(df_list):
        # 1. Enrichment Lokasi (Menghubungkan ID ke Nama)
        df = df.merge(lookup[['LocationID', 'Borough', 'Zone']], 
                      left_on='PULocationID', right_on='LocationID', how='left')
        
        # Rename agar konsisten (snake_case)
        df.rename(columns={
            'PULocationID': 'pickup_location_id',
            'DOLocationID': 'dropoff_location_id',
            'LocationID': 'location_id',
            'Borough': 'pickup_borough', 
            'Zone': 'pickup_zone'
            }, inplace=True)
        
        # 2. Enrichment Waktu (Hanya yang perlu untuk tren)
        time_col = 'tpep_pickup_datetime' if taxi_type == "yellow" else 'lpep_pickup_datetime'
        df['pickup_hour'] = df[time_col].dt.hour
        df['day_name'] = df[time_col].dt.day_name()
        df['tip_percentage'] = (df['tip_amount'] / df['fare_amount'] * 100).fillna(0).round(2)
        
        df_list[i] = df
    
    logger.info(f'Finished enrichment for {taxi_type} taxi')
    return df_list

@task(name='Enrich Weather Data')
def enrich_weather_data(df_list: list, weather_json: dict):
    # 1. Ubah JSON Daily ke DataFrame
    df_weather = pd.DataFrame(weather_json['daily'])
    # Kolom 'time' di JSON adalah tanggal (YYYY-MM-DD)
    
    for i, df in enumerate(df_list):
        # 2. Buat kolom temporary 'match_date' di data taksi (hanya tanggal)
        time_col = 'tpep_pickup_datetime' if 'tpep_pickup_datetime' in df.columns else 'lpep_pickup_datetime'
        df['match_date'] = df[time_col].dt.strftime('%Y-%m-%d')
        
        # 3. Merge dengan data cuaca
        df = df.merge(
            df_weather[['time', 'temperature_2m_max', 'precipitation_sum', 'weathercode']], 
            left_on='match_date', 
            right_on='time', 
            how='left'
        )
        df['is_raining'] = df['precipitation_sum'] > 0
        
        # 4. Hapus kolom temporary agar Silver tetap bersih
        df.drop(columns=['match_date', 'time'], inplace=True)
        df_list[i] = df
        
    return df_list

@task(name='Cleaning After Enrichment')
def clean_after_enrichment(df_list: list):
    for i, df in enumerate(df_list):
        # 1. Handling Missing Zone (Hasil Join ke taxi_zone_lookup)
        # Jika ID lokasi NULL isi dengan 'Unknown'
        if 'pickup_zone' in df.columns:
            df['pickup_zone'] = df['pickup_zone'].fillna('Unknown')
        if 'pickup_borough' in df.columns:
            df['pickup_borough'] = df['pickup_borough'].fillna('Unknown')

        # 2. Handling Missing Weather (Hasil Join ke OpenWeather JSON)
        # Jika tanggal taksi tidak ada di data cuaca, asumsi tidak hujan (0 mm)
        if 'precipitation_sum' in df.columns:
            df['precipitation_sum'] = df['precipitation_sum'].fillna(0)
        
        # Pastikan is_raining konsisten Boolean dan tidak ada yang NULL
        if 'is_raining' in df.columns:
            df['is_raining'] = df['is_raining'].fillna(False)
            
        # 3. Handling Suhu (Opsional: Isi dengan rata-rata jika ada yang kosong)
        if 'temperature_2m_max' in df.columns:
            mean_temp = df['temperature_2m_max'].mean()
            df['temperature_2m_max'] = df['temperature_2m_max'].fillna(mean_temp)

        # 4. Final Type Casting
        if 'weathercode' in df.columns:
            df['weathercode'] = df['weathercode'].fillna(-1).astype(int)

        df_list[i] = df
    
    return df_list