def store_data():
    """
    Fungsi untuk menyimpan data hasil olahan ke format Parquet final atau Database.
    """
    print("📦 [03_STORAGE] Menyimpan data ke storage final...")
    
    # Contoh logic:
    # 1. Simpan tabel DuckDB ke file 'data/processed/final_taxi_data.parquet'
    # 2. Pastikan file terkompresi agar hemat tempat
    
    print("✅ [03_STORAGE] Data berhasil diamankan di folder data/processed/")

if __name__ == "__main__":
    store_data()