# List all available commands
default:
    @just --list

# run step_01_ingestion.main.py
run:
    uv run python -m nyc_taxi.pipeline.step_01_ingestion.main