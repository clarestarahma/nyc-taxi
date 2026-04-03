# List all available commands
default:
    @just --list

# run step_05_dashboard.main.py
run:
    uv run python -m nyc_taxi.pipeline.step_05_dashboard.app