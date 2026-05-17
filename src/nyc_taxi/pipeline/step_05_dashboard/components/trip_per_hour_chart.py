import streamlit as st
import matplotlib.pyplot as plt

def show_trip_per_hour(trip_per_hour):
    fig, ax = plt.subplots(figsize=(10,5))

    ax.plot(
        trip_per_hour["pickup_hour"],
        trip_per_hour["trip_count"],
        marker="o"
    )

    ax.set_title("Trip Count per Hour")
    ax.set_xlabel("Pickup Hour")
    ax.set_ylabel("Trip Count")
    ax.grid(True)

    st.pyplot(fig)