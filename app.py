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
        data = pd.read_csv(sheet_url, dtype={"RequestNum": str})  # Ensure RequestNum is string
        st.write("### Column Names")
        st.write(data.columns)  # Display the column names for debugging
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
            # Extract latitude and longitude
            latitude = float(ticket["Latitude"])
            longitude = float(ticket["Longitude"])

            # Safely retrieve other fields with fallback for missing data
            request_num = ticket.get("RequestNum", "N/A")
            description = ticket.get("Description", "No description available")
            status = ticket.get("Status", "No status available")

            # Create popup content
            popup_content = (
                f"<b>RequestNum:</b> {request_num}<br>"
                f"<b>Description:</b> {description}<br>"
                f"<b>Status:</b> {status}"
            )

            # Add a marker to the map
            folium.Marker(
                location=[latitude, longitude],
                popup=popup_content,
                tooltip=f"Ticket: {request_num}"
            ).add_to(m)
        except (ValueError, KeyError) as e:
            st.warning(f"Skipping ticket due to invalid data: {e}")

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
    # Map/List View: Ticket List on top, Map on bottom
    st.header("Map/List View")

    # Top: Ticket List
    with st.container():
        st.subheader("Ticket List")
        st.dataframe(data, height=300)  # Scrollable list of tickets

    # Bottom: Map of Tickets
    with st.container():
        st.subheader("Tickets Map")
        map_ = plot_all_tickets(data)  # Plot all tickets on the map
        st_folium(map_, width=800, height=400)  # Adjust map size

elif menu_option == "Search Ticket":
    # Search Ticket Section
    st.header("Search Ticket by Number")
    ticket_number = st.text_input("Enter Ticket Number")

    if st.button("Search"):
        try:
            ticket_details = data[data["RequestNum"] == ticket_number.strip()]
            if not ticket_details.empty:
                st.write("### Ticket Details")
                for key, value in ticket_details.iloc[0].items():
                    st.write(f"**{key}:** {value}")
            else:
                st.warning("Ticket not found.")
        except KeyError:
            st.error("Error: 'RequestNum' column not found.")
