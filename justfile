# List all available commands
default:
    @just --list

# Run the ENTIRE pipeline dari main utama
run-all:
    uv run python -m nyc_taxi.main

# Setup environment dan install dependencies
setup:
    uv sync

# Show all raw file
all_raw:
    uv run python -m nyc_taxi.pipeline.step_02_preprocessing.main show

# Run Prefect Server
server:
    uv run prefect server start

# Run Data Ingestion (Step 01)
ingest:
    uv run python -m nyc_taxi.pipeline.step_01_ingestion.main

# Run Data Preprocessing (Step 02)
process:
    uv run python -m nyc_taxi.pipeline.step_02_preprocessing.main

# Run Data Storage (Step 03)
store:
    uv run python -m nyc_taxi.pipeline.step_03_storage.main

# Run Dashboard (Streamlit agak beda cara panggilnya)
dashboard:
    uv run streamlit run src/nyc_taxi/pipeline/step_05_dashboard/app.py