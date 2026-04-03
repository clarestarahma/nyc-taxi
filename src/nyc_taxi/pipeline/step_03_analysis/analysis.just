# List all available commands
default:
    @just --list

# run step_03_analysis.main.py
run:
    uv run python -m nyc_taxi.pipeline.step_03_analysis.main