import streamlit as st

def render_metric_cards(df):
  """ Komponen untuk menampilkan ringkasan metrik di atas peta """

#   print(df.columns)
  
  # Hitung metrik utamanya
  total_revenue = df["total_revenue"].sum()
  total_trips = df["trip_count"].sum()
  avg_tips = df["avg_tip"].mean()

  c1, c2, c3 = st.columns(3)
  
  with c1:
      st.metric(label="Total Revenue", value=f"${total_revenue:,.0f}")
  with c2:
      st.metric(label="Total Trips", value=f"{total_trips:,}")
  with c3:
      st.metric(label="Avg Tips", value=f"${avg_tips:.2f}")
  
#   st.markdown("---")