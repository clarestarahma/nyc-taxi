import streamlit as st
import matplotlib.pyplot as plt

def show_rain_trip_chart(rain_analysis):
    fig, ax = plt.subplots(figsize=(6,4))

    ax.bar(
        rain_analysis["is_raining"].astype(str),
        rain_analysis["trip_count"]
    )

    ax.set_title("Trip Count based on Rain")
    ax.set_xlabel("Is Raining")
    ax.set_ylabel("Trip Count")

    st.pyplot(fig)