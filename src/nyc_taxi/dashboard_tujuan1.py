from pathlib import Path
import json
import copy

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st


# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="NYC Taxi Dashboard",
    page_icon="🚕",
    layout="wide",
)

ROOT_DIR = Path(__file__).resolve().parents[2]
ZONE_PATH = ROOT_DIR / "data" / "gold" / "zone_profitability.csv"
GEOJSON_PATH = ROOT_DIR / "data" / "static" / "NYC Taxi Zones.geojson"

METRIC_LABELS = {
    "total_revenue": "Total Revenue",
    "avg_fare": "Average Fare",
    "avg_tip": "Average Tip",
    "trip_count": "Trip Count",
}


# =========================
# HELPERS
# =========================
@st.cache_data
def load_zone_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    df = pd.read_csv(path)

    numeric_cols = ["trip_count", "total_revenue", "avg_fare", "avg_tip", "pickup_location_id"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["zone", "borough", "service_type"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    return df


@st.cache_data
def load_geojson(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def get_fill_color(value: float, vmin: float, vmax: float) -> list[int]:
    if vmax == vmin:
        ratio = 0.0
    else:
        ratio = (value - vmin) / (vmax - vmin)

    ratio = max(0.0, min(1.0, ratio))

    # gradasi biru muda -> biru tua yang lebih kontras
    start = (219, 234, 254)   # light blue
    end = (37, 99, 235)       # strong blue

    r = int(start[0] + (end[0] - start[0]) * ratio)
    g = int(start[1] + (end[1] - start[1]) * ratio)
    b = int(start[2] + (end[2] - start[2]) * ratio)

    return [r, g, b, 190]


def build_map_geojson(geojson_raw, filtered_df: pd.DataFrame, metric: str):
    geojson = copy.deepcopy(geojson_raw)
    df_map = filtered_df.copy()

    df_map = df_map.dropna(subset=["pickup_location_id"]).copy()
    df_map["pickup_location_id"] = df_map["pickup_location_id"].astype("Int64").astype(str)

    value_map = df_map.set_index("pickup_location_id")[metric].to_dict()

    values = list(value_map.values())
    if len(values) == 0:
        vmin, vmax = 0, 1
    else:
        vmin, vmax = min(values), max(values)

    for feature in geojson["features"]:
        loc_id = str(feature["properties"].get("location_id"))
        value = float(value_map.get(loc_id, 0))

        zone_name = feature["properties"].get("zone", "Unknown")
        borough_name = feature["properties"].get("borough", "Unknown")

        feature["metric_value"] = round(value, 2)
        feature["fill_color"] = get_fill_color(value, vmin, vmax)
        feature["zone_name"] = zone_name
        feature["borough_name"] = borough_name

        if metric == "trip_count":
            feature["metric_display"] = f"{value:,.0f}"
        else:
            feature["metric_display"] = f"${value:,.2f}"

    return geojson


# =========================
# LOAD DATA
# =========================
try:
    zone_df = load_zone_data(ZONE_PATH)
    geojson_raw = load_geojson(GEOJSON_PATH)
except Exception as e:
    st.error(f"Gagal membaca data: {e}")
    st.stop()


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🚕 NYC Taxi")
    st.caption("Dashboard analisis zona revenue. Halaman lain dikosongi agar bisa dilanjutkan oleh anggota tim lain.")

    page = st.radio(
        "Pilih Halaman",
        ["Zona Revenue", "Pengaruh Cuaca", "Prediksi Trip"],
    )


# =========================
# PAGE 1: ZONA REVENUE
# =========================
if page == "Zona Revenue":
    st.title("Zona Operasi Paling Menguntungkan")
    st.caption("Analisis zona pickup berdasarkan total revenue, average fare, average tip, dan trip count.")

    # ---------- FILTER ----------
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        taxi_type = st.selectbox("Tipe Taxi", ["Semua", "Yellow", "Green"])

    with c2:
        metric = st.selectbox(
            "Metrik Utama",
            ["total_revenue", "avg_fare", "avg_tip", "trip_count"],
            format_func=lambda x: METRIC_LABELS[x],
        )

    with c3:
        top_n = st.slider("Jumlah Zona Ditampilkan", min_value=5, max_value=20, value=10)

    borough_options = sorted(zone_df["borough"].dropna().unique().tolist())
    selected_boroughs = st.multiselect(
        "Filter Borough",
        borough_options,
        default=borough_options,
    )

    search_zone = st.text_input("Cari nama zona (opsional)", placeholder="misalnya: JFK, Midtown, Newark")

    # ---------- APPLY FILTER ----------
    filtered = zone_df.copy()

    if taxi_type != "Semua":
        filtered = filtered[filtered["service_type"] == taxi_type]

    if selected_boroughs:
        filtered = filtered[filtered["borough"].isin(selected_boroughs)]

    if search_zone:
        filtered = filtered[filtered["zone"].str.contains(search_zone, case=False, na=False)]

    if filtered.empty:
        st.warning("Tidak ada data yang cocok dengan filter.")
        st.stop()

    # ---------- SUMMARY ----------
    total_revenue = filtered["total_revenue"].sum()
    total_trips = filtered["trip_count"].sum()
    avg_fare = weighted_average(filtered, "avg_fare")
    avg_tip = weighted_average(filtered, "avg_tip")

    top_zone_metric = filtered.sort_values(metric, ascending=False).iloc[0]
    top_zone_revenue = filtered.sort_values("total_revenue", ascending=False).iloc[0]
    top_zone_tip = filtered.sort_values("avg_tip", ascending=False).iloc[0]
    top_borough = (
        filtered.groupby("borough", as_index=False)["total_revenue"]
        .sum()
        .sort_values("total_revenue", ascending=False)
        .iloc[0]
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", money(total_revenue))
    m2.metric("Total Trips", f"{total_trips:,.0f}")
    m3.metric("Average Fare", money(avg_fare))
    m4.metric("Average Tip", money(avg_tip))

    # ---------- HIGHLIGHT + TOP CHART ----------
    left, right = st.columns([1.15, 1])

    with left:
        st.subheader("Highlight Zona")
        st.info(
            f"""
**Zona teratas berdasarkan {METRIC_LABELS[metric]}:** {top_zone_metric['zone']}  
**Borough:** {top_zone_metric['borough']}  
**Tipe Taxi:** {top_zone_metric['service_type']}  
**Nilai:** {money(top_zone_metric[metric]) if metric != 'trip_count' else f"{top_zone_metric[metric]:,.0f}"}
"""
        )

        st.markdown("**Insight singkat:**")
        st.write(f"- Zona dengan **total revenue tertinggi**: **{top_zone_revenue['zone']}** ({money(top_zone_revenue['total_revenue'])})")
        st.write(f"- Zona dengan **average tip tertinggi**: **{top_zone_tip['zone']}** ({money(top_zone_tip['avg_tip'])})")
        st.write(f"- **Borough** dengan revenue tertinggi: **{top_borough['borough']}** ({money(top_borough['total_revenue'])})")

    with right:
        st.subheader("Top Zona — Total Revenue")
        top_revenue_df = filtered.sort_values("total_revenue", ascending=False).head(top_n)

        chart_top_revenue = (
            alt.Chart(top_revenue_df)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                x=alt.X("total_revenue:Q", title="Total Revenue"),
                y=alt.Y(
                    "zone:N",
                    sort="-x",
                    title=None,
                    axis=alt.Axis(labelLimit=180),
                ),
                color=alt.Color(
                    "service_type:N",
                    scale=alt.Scale(
                        domain=["Yellow", "Green"],
                        range=["#FACC15", "#10B981"],
                    ),
                    title="Tipe Taxi",
                ),
                tooltip=[
                    alt.Tooltip("zone:N", title="Zona"),
                    alt.Tooltip("borough:N", title="Borough"),
                    alt.Tooltip("service_type:N", title="Tipe"),
                    alt.Tooltip("total_revenue:Q", title="Total Revenue", format=",.2f"),
                    alt.Tooltip("trip_count:Q", title="Trip Count", format=",.0f"),
                    alt.Tooltip("avg_fare:Q", title="Avg Fare", format=",.2f"),
                    alt.Tooltip("avg_tip:Q", title="Avg Tip", format=",.2f"),
                ],
            )
            .properties(height=380)
        )

        st.altair_chart(style_chart(chart_top_revenue), use_container_width=True)

    # ---------- TWO CHARTS ----------
    c_left, c_right = st.columns(2)

    with c_left:
        st.subheader(f"Ranking Berdasarkan {METRIC_LABELS[metric]}")
        ranked_metric = filtered.sort_values(metric, ascending=False).head(top_n)

        chart_metric = (
            alt.Chart(ranked_metric)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#2563EB")
            .encode(
                x=alt.X(f"{metric}:Q", title=METRIC_LABELS[metric]),
                y=alt.Y(
                    "zone:N",
                    sort="-x",
                    title=None,
                    axis=alt.Axis(labelLimit=180),
                ),
                tooltip=[
                    alt.Tooltip("zone:N", title="Zona"),
                    alt.Tooltip("borough:N", title="Borough"),
                    alt.Tooltip("service_type:N", title="Tipe"),
                    alt.Tooltip(f"{metric}:Q", title=METRIC_LABELS[metric], format=",.2f"),
                ],
            )
            .properties(height=380)
        )

        st.altair_chart(style_chart(chart_metric), use_container_width=True)

    with c_right:
        st.subheader("Revenue per Borough")
        borough_df = (
            filtered.groupby("borough", as_index=False)
            .agg(total_revenue=("total_revenue", "sum"))
            .sort_values("total_revenue", ascending=False)
        )

        chart_borough = (
            alt.Chart(borough_df)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color="#10B981")
            .encode(
                x=alt.X(
                    "borough:N",
                    sort="-y",
                    title=None,
                    axis=alt.Axis(labelAngle=-35, labelLimit=140),
                ),
                y=alt.Y("total_revenue:Q", title="Total Revenue"),
                tooltip=[
                    alt.Tooltip("borough:N", title="Borough"),
                    alt.Tooltip("total_revenue:Q", title="Total Revenue", format=",.2f"),
                ],
            )
            .properties(height=380)
        )

        st.altair_chart(style_chart(chart_borough), use_container_width=True)

    # ---------- MAP ----------
        # ---------- MAP ----------
    st.subheader("Peta Zona Berdasarkan Metrik Terpilih")

    map_geojson = build_map_geojson(geojson_raw, filtered, metric)

    tooltip = {
        "text": f"Zona: {{zone_name}}\nBorough: {{borough_name}}\n{METRIC_LABELS[metric]}: {{metric_display}}"
    }

    layer = pdk.Layer(
        "GeoJsonLayer",
        data=map_geojson,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=False,
        get_fill_color="fill_color",
        get_line_color=[255, 255, 255, 150],
        line_width_min_pixels=1.5,
    )

    view_state = pdk.ViewState(
        latitude=40.72,
        longitude=-73.94,
        zoom=9.6,
        pitch=0,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_provider="carto",
        map_style="light",
        height=560,
    )

    st.pydeck_chart(deck, use_container_width=True)

    # ---------- TABLE ----------
    st.subheader("Tabel Ringkasan Zona")

    table_df = filtered.sort_values("total_revenue", ascending=False).reset_index(drop=True)

    st.dataframe(
        table_df[
            ["service_type", "zone", "borough", "trip_count", "total_revenue", "avg_fare", "avg_tip"]
        ],
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    st.download_button(
        "Download hasil filter",
        data=table_df.to_csv(index=False).encode("utf-8"),
        file_name="zone_profitability_filtered.csv",
        mime="text/csv",
    )


# =========================
# PAGE 2: PENGARUH CUACA
# =========================
elif page == "Pengaruh Cuaca":
    st.title("Pengaruh Cuaca")
    st.info("Halaman ini sengaja dikosongi agar bisa diisi oleh teman Anda.")
    st.write("")
    st.write("Silakan nanti tambahkan analisis, chart, dan filter sesuai kebutuhan tim.")


# =========================
# PAGE 3: PREDIKSI TRIP
# =========================
elif page == "Prediksi Trip":
    st.title("Prediksi Trip")
    st.info("Halaman ini sengaja dikosongi agar bisa diisi oleh teman Anda.")
    st.write("")
    st.write("Silakan nanti tambahkan model, input prediksi, dan hasil evaluasi di halaman ini.")