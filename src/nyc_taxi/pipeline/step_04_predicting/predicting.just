# List all available commands
default:
    @just --list

# run step_04_predicting.main.py
run:
    uv run python -m nyc_taxi.pipeline.step_04_predicting.main