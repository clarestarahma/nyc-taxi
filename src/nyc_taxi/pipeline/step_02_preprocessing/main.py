import duckdb
import pandas as pd
from nyc_taxi.config import settings

def preprocess_data():
    """
    Fungsi untuk membersihkan data mentah menggunakan SQL/DuckDB.
    """
    print("🧹 [02_PREPROCESSING] Memulai pembersihan data...")
    

    with duckdb.connect(settings.RAW_DB_PATH) as conn:
        try:
            df_y = conn.execute("SELECT * FROM raw.yellow_taxi").df()
            df_g = conn.execute("SELECT * FROM raw.green_taxi").df()
            df_fhv = conn.execute("SELECT * FROM raw.fhv_taxi").df()
            df_hvfhv = conn.execute("SELECT * FROM raw.hvfhv_taxi").df()
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 1000)
            # INI CUMA NYOBA BUAT LIHAT DATA DI /data/nyc_taxi.db
            # 3. Cek hasilnya
            print(f"✅ Data berhasil dimuat ke DataFrame!")

            print(f"Data YELLOW Taxi")
            print(f"Shape: {df_y.shape}")
            print(df_y.head(), "\n")

            print(f"Data GREEN Taxi")
            print(f"Shape: {df_g.shape}")
            print(df_g.head(), "\n")

            print(f"Data FHV Taxi")
            print(f"Shape: {df_fhv.shape}")
            print(df_fhv.head(), "\n")

            print(f"Data HVFHV Taxi")
            print(f"Shape: {df_hvfhv.shape}")
            print(df_hvfhv.head(), "\n")
        except Exception as e:
            print("Gagal menampilkan data: {e}")
    
    print("✅ [02_PREPROCESSING] Data telah bersih dan siap untuk disimpan.")

if __name__ == "__main__":
    preprocess_data()