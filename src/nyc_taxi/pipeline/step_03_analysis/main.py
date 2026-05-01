from .flow.gold_profitability_flow import gold_profitability_flow

def analysis_data():
    print("📊 [04_ANALYSIS] Running Data Analysis: Calculating Trip Trends...")
    gold_profitability_flow()

if __name__ == "__main__":
    analysis_data()