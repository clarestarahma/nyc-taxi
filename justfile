# ingestion
mod ingestion "src/nyc_taxi/pipeline/step_01_ingestion/ingestion.just"
# preprocessing
mod preprocessing "src/nyc_taxi/pipeline/step_02_preprocessing/preprocessing.just"
# analysis
mod analysis "src/nyc_taxi/pipeline/step_03_analysis/analysis.just"
# predicting
mod predicting "src/nyc_taxi/pipeline/step_04_predicting/predicting.just"
# dashboard
mod dashboard "src/nyc_taxi/pipeline/step_05_dashboard/dashboard.just"

set shell:=["powershell.exe", "-c"]

# List all available commands
default:
    @just --list

# Run the ENTIRE pipeline dari main utama
run-all:
    uv run python -m nyc_taxi.main

# Setup environment dan install dependencies
setup:
    uv sync

# Run the Streamlit dashboard for data inspection (default)
inspect:
    uv run streamlit run inspect_db.py

# Clear Streamlit cache and restart the dashboard
inspect-clean:
    rm -rf ~/.streamlit/cache
    uv run streamlit run inspect_db.py

# Start Prefect server (run this in terminal 1)
server:
    uv run prefect server start