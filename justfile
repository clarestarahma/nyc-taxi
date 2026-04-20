set shell := ["bash", "-c"]

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

<<<<<<< Updated upstream
=======
set shell := ["powershell.exe", "-c"]
>>>>>>> Stashed changes

# List all available commands
default:
    @just --list


# Setup environment Kaggle (Hanya jalankan sekali)
setup-kaggle:
    rm -rf ~/.kaggle
    mkdir -p ~/.kaggle
    cp kaggle.json ~/.kaggle/
    chmod 600 ~/.kaggle/kaggle.json
    @echo "Kaggle API key berhasil dikonfigurasi."

# Download dan ekstrak dataset secara otomatis
download-data-geojson: setup-kaggle
    rm -rf data/
    mkdir -p data/static
    uv run kaggle datasets download mxruedag/tlc-nyc-taxi-zones
    unzip -o tlc-nyc-taxi-zones.zip -d data/static
    rm tlc-nyc-taxi-zones.zip
    rm data/static/taxi_zones.csv
    @echo "Dataset berhasil didownload dan diekstrak ke folder data/static"

# Run the ENTIRE pipeline dari main utama
run-all: download-data-geojson
    uv run python -m nyc_taxi.main

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