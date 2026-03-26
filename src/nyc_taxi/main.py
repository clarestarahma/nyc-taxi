from nyc_taxi.pipeline.step_01_ingestion.main import ingest_data
from nyc_taxi.pipeline.step_02_preprocessing.main import preprocess_data
from nyc_taxi.pipeline.step_03_storage.main import store_data
from nyc_taxi.pipeline.step_04_analysis.main import run_analysis

def run_pipeline():
    print("--- 🚕 NYC TAXI DATA PIPELINE INTERNAL BOOTSTRAP 🚕 ---")
    
    # Menjalankan urutan tahap demi tahap
    ingest_data()
    preprocess_data()
    store_data()
    run_analysis()
    
    print("--- ✅ ALL INTERNAL STAGES COMPLETED ---")

if __name__ == "__main__":
    run_pipeline()