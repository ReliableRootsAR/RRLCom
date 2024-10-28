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
    return pd.read_csv(sheet_url)

# Load the data from the Google Sheet
data = load_data()

# Function to search for ticket details by ticket number
def get_ticket_details(ticket_number):
    """Retrieve ticket details based on ticket number."""
    ticket = data[data["Ticket Number"].astype(str) == ticket_number]
    if ticket.empty:
        return None
    return ticket.iloc[0].to_dict()

# Function to plot tickets on a map
def plot_map(tickets):
    """Create a map with markers for active tickets."""
    map_center = [38.9717, -95.2353]  # Example: Lawrence, KS
    m = folium.Map(location=map_center, zoom_start=12)

    for _, ticket in tickets.iterrows():
        folium.Marker(
            location=[ticket["Latitude"], ticket["Longitude"]],
            popup=f'Ticket: {ticket["Ticket Number"]}',
            tooltip=ticket["Description"],
        ).add_to(m)

    return m

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
    active_tickets = data[data["Status"] == "Active"]

    if active_tickets.empty:
        st.warning("No active tickets available.")
    else:
        st_folium(plot_map(active_tickets))

