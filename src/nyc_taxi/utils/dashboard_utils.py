import pandas as pd

METRIC_LABELS = {
    "total_revenue": "Total Revenue",
    "avg_fare": "Average Fare",
    "avg_tip": "Average Tip",
    "trip_count": "Trip Count",
}

def weighted_average(df: pd.DataFrame, value_col: str, weight_col: str = "trip_count") -> float:
    if df.empty or df[weight_col].sum() == 0:
        return 0.0
    return (df[value_col] * df[weight_col]).sum() / df[weight_col].sum()


def money(x: float) -> str:
    return f"${x:,.2f}"


def style_chart(chart):
    return (
        chart
        .configure(background="white")
        .configure_axis(
            labelColor="#111827",
            titleColor="#111827",
            gridColor="#E5E7EB",
            domainColor="#D1D5DB",
            tickColor="#D1D5DB",
            labelFontSize=11,
            titleFontSize=12,
        )
        .configure_legend(
            labelColor="#111827",
            titleColor="#111827",
            labelFontSize=11,
            titleFontSize=12,
        )
        .configure_title(
            color="#111827",
            fontSize=14,
            anchor="start",
        )
        .configure_view(strokeWidth=0)
    )