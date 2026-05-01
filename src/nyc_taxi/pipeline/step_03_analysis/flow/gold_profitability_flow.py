from prefect import flow
from ..tasks.gold_profitability import fetch_zone_profitability
from ..tasks.transform_profitability import enrich_with_location_id
from ..tasks.load_gold import load_zone_profitability

@flow
def gold_profitability_flow():
    df = fetch_zone_profitability()
    df = enrich_with_location_id(df)
    load_zone_profitability(df)