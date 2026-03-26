import streamlit as st

def main():
    st.set_page_config(page_title="NYC Taxi Dashboard", page_icon="🚕")
    st.title("NYC Taxi Analytics Dashboard 🚕")
    st.write("Welcome, Team! This is our project visualization area.")
    
    # Contoh metrics sederhana
    col1, col2 = st.columns(2)
    col1.metric("Total Trips", "1.2M")
    col2.metric("Avg. Fare", "$15.50")

if __name__ == "__main__":
    main()