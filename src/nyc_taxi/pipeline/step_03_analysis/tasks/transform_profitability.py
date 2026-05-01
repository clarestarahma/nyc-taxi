from prefect import task
import pandas as pd
from nyc_taxi.config.settings import STATIC_DIR

@task
def enrich_with_location_id(df):
    lookup = pd.read_csv(STATIC_DIR / "taxi_zone_lookup.csv")

    if "pickup_location_id" not in df.columns:
        df = df.merge(
            lookup[["LocationID", "Borough", "Zone"]],
            left_on=["borough", "zone"],
            right_on=["Borough", "Zone"],
            how="left"
        ).rename(columns={"LocationID": "pickup_location_id"})

    return df