import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Public Google Sheet URL (export as CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqZXXI_jWbUVc/export?format=csv"

# Cache the data to improve performance
@st.cache_data
def load_data():
    """Load the ticket data from the Google Sheet."""
    try:
        data = pd.read_csv(sheet_url, dtype={"RequestNum": str})  # Ensure RequestNum is a string
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
data = load_data()

# Function to plot all tickets on a map
def plot_all_tickets(tickets):
    """Create a map with markers for all tickets."""
    map_center = [38.9717, -95.2353]  # Default map center (Lawrence, KS)
    m = folium.Map(location=map_center, zoom_start=12)

    for _, ticket in tickets.iterrows():
        try:
            latitude = float(ticket["Latitude"])
            longitude = float(ticket["Longitude"])
            popup_content = (
                f"<b>RequestNum:</b> {ticket['RequestNum']}<br>"
                f"<b>Description:</b> {ticket['Description']}<br>"
                f"<b>Status:</b> {ticket['Status']}"
            )
            folium.Marker(
                location=[latitude, longitude],
                popup=popup_content,
                tooltip=f"Ticket: {ticket['RequestNum']}"
            ).add_to(m)
        except (ValueError, KeyError) as e:
            st.warning(f"Skipping ticket due to invalid coordinates or data: {e}")

    return m

# Streamlit App UI
st.title("RRLCom - Ticket Management System")

# Sidebar for navigation
st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox(
    "Select an option:",
    ["List View", "Map/List View", "Search Ticket"]
)

if menu_option == "List View":
    # List View: Display all tickets in a scrollable table
    st.header("All Tickets")
    st.dataframe(data)  # Display all tickets in a DataFrame-like view

elif menu_option == "Map/List View":
    # Map/List View: Top - List of Tickets, Bottom - Map of Tickets
    st.header("Map/List View")

    # Create two vertical sections: one for the list and one for the map
    with st.container():
        st.subheader("Ticket List")
        # Use st.dataframe to display a scrollable list of tickets
        st.dataframe(data, height=300)  # Limit height for better scrolling

    with st.container():
        st.subheader("Tickets Map")
        map_ = plot_all_tickets(data)  # Plot all tickets on the map
        st_folium(map_, width=800, height=400)  # Adjust map size

elif menu_option == "Search Ticket":
    # Search Ticket Section
    st.header("Search Ticket by Number")
    ticket_number = st.text_input("Enter Ticket Number")

    if st.button("Search"):
        ticket_details = data[data["RequestNum"] == ticket_number.strip()]
        if not ticket_details.empty:
            st.write("### Ticket Details")
            for key, value in ticket_details.iloc[0].items():
                st.write(f"**{key}:** {value}")
        else:
            st.warning("Ticket not found.")
