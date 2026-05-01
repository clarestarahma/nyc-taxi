import streamlit as st
import altair as alt
import pandas as pd

def render_borough_analysis(df, metric, metric_label, top_n):
    """Komponen adaptif yang memilih chart terbaik berdasarkan jenis metrik"""

    is_average = any(word in metric.lower() for word in ["average", "fare", "tip"])

    if is_average:
        borough_data = df.groupby('borough')[metric].mean().reset_index()
        label_tengah = "Avg Global"
    else:
        borough_data = df.groupby('borough')[metric].sum().reset_index()
        label_tengah = "Total"

    # 2. FILTER TOP N
    borough_data = borough_data.nlargest(top_n, metric)

    display_val = borough_data[metric].mean() if is_average else borough_data[metric].sum()

    if borough_data.empty:
        st.info("Data tidak tersedia.")
        return

    if not is_average:
        # Bar Chart Horizontal (untuk Revenue/Count)
        st.write(f"### 📊 Diagram Batang ({top_n} Teratas)")
        # Layer 1: Batang
        base = alt.Chart(borough_data).encode(
            x=alt.X(f"{metric}:Q", title=metric_label),
            y=alt.Y("borough:N", sort='-x', title="Borough", axis=alt.Axis(labelAngle=0)),
            color=alt.Color("borough:N", legend=None),
            tooltip=['borough', alt.Tooltip(f'{metric}:Q', format=',.0f')]
        )
        bars = base.mark_bar(cornerRadiusEnd=4)

        # Layer 2: Teks di ujung batang
        text = base.mark_text(
            align='left',
            baseline='middle',
            dx=5,
            fontWeight='bold',
            color='white'
        ).encode(
            text=alt.Text(f'{metric}:Q', format='.2s')
        )

        # Tinggi dinamis: makin banyak top_n, makin tinggi grafiknya
        # dynamic_height = 150 + (top_n * 30)
        st.altair_chart((bars + text).properties(height=425), width='stretch')
    else:
        # Diagram lingkaran
        st.write(f"### 🍩 Diagram Lingkaran ({top_n} Teratas)")
        
        base = alt.Chart(borough_data).encode(
            theta=alt.Theta(field=metric, type="quantitative"),
            color=alt.Color(
                "borough:N", 
                legend=alt.Legend(
                    orient="bottom", 
                    columns=2,
                    symbolType='circle',
                    symbolSize=180,
                    symbolStrokeWidth=0,
                    labelFontSize=14,
                    labelPadding=10,
                    titleFontSize=15
                )
            )
        )
        
        donut = base.mark_arc(
            innerRadius=80, 
            outerRadius=120, 
            stroke="white", 
            strokeWidth=1.5,
            opacity=1
        )
        
        # Angka di tengah (font diperbesar agar proporsional)
        center_number = alt.Chart(pd.DataFrame({'text': [f"{display_val:,.1f}"]})).mark_text(
            fontSize=30, fontWeight='bold', color='#FFD700'
        ).encode(text='text:N')
        
        center_label = alt.Chart(pd.DataFrame({'text': [label_tengah]})).mark_text(
            dy=30, fontSize=14, color='white'
        ).encode(text='text:N')

        st.altair_chart(
            (donut + center_number + center_label).properties(height=450), 
            width='stretch'
        )

    # Insight singkat
    top_b = borough_data.iloc[0]
    st.info(f"💡 **{top_b['borough']}** menduduki peringkat pertama dengan {top_b[metric]:,.1f}.")