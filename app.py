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
        data = pd.read_csv(sheet_url, dtype={"RequestNum": str})  # Ensure ticket numbers are strings
        st.write("### Data Preview")
        st.write(data.head())  # Show the first few rows for verification
        st.write("### Column Names")
        st.write(data.columns)  # Display column names for debugging
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if loading fails

# Load the data from the Google Sheet
data = load_data()

# Function to search for ticket details by ticket number
def get_ticket_details(ticket_number):
    """Retrieve ticket details based on RequestNum."""
    try:
        ticket_number = ticket_number.strip()  # Clean up any spaces
        ticket = data[data["RequestNum"] == ticket_number]  # Use the correct column name
        if ticket.empty:
            return None
        return ticket.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Error retrieving ticket details: {e}")
        return None

# Function to plot tickets on a map
def plot_map(tickets):
    """Create a map with markers for active tickets."""
    try:
        map_center = [38.9717, -95.2353]  # Default: Lawrence, KS
        m = folium.Map(location=map_center, zoom_start=12)

        for _, ticket in tickets.iterrows():
            try:
                latitude = float(ticket["Latitude"])
                longitude = float(ticket["Longitude"])
                folium.Marker(
                    location=[latitude, longitude],
                    popup=f'Ticket: {ticket["RequestNum"]}',
                    tooltip=ticket["Description"],
                ).add_to(m)
            except (ValueError, KeyError) as e:
                st.warning(f"Skipping ticket due to invalid coordinates or data: {e}")

        return m
    except Exception as e:
        st.error(f"Error creating the map: {e}")
        return None

# Streamlit App UI
st.title("RRLCom - Ticket Management System")

# Sidebar for navigation
st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox(
    "Select an option:",
    ["Search Ticket", "Active Tickets Map"]
)

if menu_option == "Search Ticket":
    # Search Ticket Section
    st.header("Search Ticket by Number")
    ticket_number = st.text_input("Enter Ticket Number")

    if st.button("Search"):
        ticket_details = get_ticket_details(ticket_number)
        if ticket_details:
            st.write("### Ticket Details")
            for key, value in ticket_details.items():
                st.write(f"**{key}:** {value}")
        else:
            st.warning("Ticket not found.")

elif menu_option == "Active Tickets Map":
    # Active Tickets Map Section
    st.header("Active Tickets Map")
    if "Status" not in data.columns:
        st.error("Column 'Status' not found in the data.")
    else:
        active_tickets = data[data["Status"] == "Active"]

        if active_tickets.empty:
            st.warning("No active tickets available.")
        else:
            map_ = plot_map(active_tickets)
            if map_:
                st_folium(map_)
