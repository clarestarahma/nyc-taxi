from nyc_taxi.pipeline.step_01_ingestion.main import ingest_data
from nyc_taxi.pipeline.step_02_preprocessing.main import preprocess_data
from nyc_taxi.pipeline.step_03_analysis.main import run_analysis
import logging

def run_pipeline():
    logger = logging.getLogger(__name__)
    logger.info("--- 🚕 NYC TAXI DATA PIPELINE INTERNAL BOOTSTRAP 🚕 ---")
    
    # Menjalankan urutan tahap demi tahap
    ingest_data()
    preprocess_data()
    run_analysis()
    # nanti dilengkapi
    
    logger.info("--- ✅ ALL INTERNAL STAGES COMPLETED ---")

if __name__ == "__main__":
    run_pipeline()