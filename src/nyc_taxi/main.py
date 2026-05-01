# from nyc_taxi.pipeline.step_01_ingestion.main import ingest_all_taxi_data
from nyc_taxi.pipeline.step_01_ingestion.main import ingest_data
from nyc_taxi.pipeline.step_02_preprocessing.main import preprocessing_data
from nyc_taxi.pipeline.step_03_analysis.main import analysis_data
from nyc_taxi.pipeline.step_04_predicting.main import predicting_data

import logging
from prefect import flow

@flow(name="NYC Taxi Main Pipeline")
def run_pipeline():
    logger = logging.getLogger(__name__)
    logger.info("--- 🚕 NYC TAXI DATA PIPELINE INTERNAL BOOTSTRAP 🚕 ---")
    
    # Menjalankan urutan tahap demi tahap
    ingest_data()
    preprocessing_data()
    analysis_data()
    # predicting_data

    
    logger.info("--- ✅ ALL INTERNAL STAGES COMPLETED ---")

if __name__ == "__main__":
    run_pipeline()