# ingestion
mod ingestion "src/nyc_taxi/pipeline/step_01_ingestion/ingestion.just"
mod preprocessing "src/nyc_taxi/pipeline/step_02_preprocessing/preprocessing.just"
mod analysis "src/nyc_taxi/pipeline/step_03_analysis/analysis.just"
mod predicting "src/nyc_taxi/pipeline/step_04_predicting/predicting.just"
mod dashboard "src/nyc_taxi/pipeline/step_05_dashboard/dashboard.just"

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