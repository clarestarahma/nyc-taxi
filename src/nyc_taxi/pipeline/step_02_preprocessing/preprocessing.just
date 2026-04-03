# List all available commands
default:
    @just --list

# run step_02_preprocessing.main.py
run:
    uv run python -m nyc_taxi.pipeline.step_02_preprocessing.main

# Show all raw file
all_raw:
    uv run python -m nyc_taxi.pipeline.step_02_preprocessing.main show