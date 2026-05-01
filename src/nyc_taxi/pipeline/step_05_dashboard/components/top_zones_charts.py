import streamlit as st
import altair as alt

def render_top_zones_chart(df, metric, metric_label, top_n):
    """Menampilkan 10 zona teratas dengan logika visualisasi adaptif"""
    st.write(f"### 🏆 Top {top_n} Zona ({metric_label})")
    
    zone_data = df.groupby(['zone', 'borough'])[metric].sum().reset_index() if "average" not in metric.lower() \
                else df.groupby(['zone', 'borough'])[metric].mean().reset_index()

    # Ambil 10 data terbesar untuk metrik tersebut
    top_zones = zone_data.nlargest(top_n, metric)

    # Tentukan apakah metrik ini bersifat rata-rata atau akumulatif
    is_average = "average" in metric.lower() or "fare" in metric.lower() or "tip" in metric.lower()

    if not is_average:
        # Untuk Revenue & Trip Count: Bar Chart fokus pada volume (besaran batang)
        chart = alt.Chart(top_zones).mark_bar(color="#1D4ED8", cornerRadiusEnd=4).encode(
            x=alt.X(f"{metric}:Q", title=metric_label),
            y=alt.Y("zone:N", sort="-x", title="Zona"),
            tooltip=["zone", "borough", alt.Tooltip(f"{metric}:Q", format=",.2f")]
        ).properties(height=425)
    else:
        # Untuk Average Fare/Tip: Gunakan Bar Chart dengan warna gradasi 
        # untuk menunjukkan 'kualitas' atau 'intensitas' rata-rata di zona tersebut
        chart = alt.Chart(top_zones).mark_bar().encode(
            x=alt.X(f"{metric}:Q", title=metric_label),
            y=alt.Y("zone:N", sort="-x", title="Zona"),
            color=alt.Color(f"{metric}:Q", scale=alt.Scale(scheme='blues'), legend=None),
            tooltip=["zone", "borough", alt.Tooltip(f"{metric}:Q", format=",.2f")]
        ).properties(height=425)

    # Tambahkan label teks angka di ujung batang agar informatif
    text = chart.mark_text(
        align='left',
        baseline='middle',
        dx=5
    ).encode(
        text=alt.Text(f'{metric}:Q', format='.2f')
    )

    st.altair_chart(chart + text, width='stretch')