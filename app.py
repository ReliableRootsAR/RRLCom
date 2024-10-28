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

# Function to plot tickets on a map
def plot_map(tickets):
    """Create an interactive map with markers for tickets."""
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

# Function to display the message input and reply section
def message_section(request_num):
    """Message system for sending and replying to messages."""
    st.subheader(f"Messages for Ticket: {request_num}")
    message = st.text_area("Enter your message:")
    if st.button("Send Message"):
        # For now, just simulate sending a message (can store messages later)
        st.success(f"Message sent for Ticket {request_num}: {message}")

# Streamlit App UI
st.title("RRLCom - Ticket Management System")

# Sidebar for navigation
st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox(
    "Select an option:",
    ["List View", "Split View", "Search Ticket"]
)

if menu_option == "List View":
    # List View of All Tickets
    st.header("All Tickets")
    st.dataframe(data)  # Display all tickets in a table-like view

elif menu_option == "Split View":
    # Split View: List View on Top, Map Below
    st.header("Tickets Overview (List and Map)")

    # Create two columns: one for list view, one for the map
    top, bottom = st.columns([1, 2])

    # List view in the top section
    with top:
        selected_ticket = st.selectbox("Select a Ticket:", data["RequestNum"])
        ticket_details = data[data["RequestNum"] == selected_ticket].iloc[0]
        st.write(f"### Ticket Details for {selected_ticket}")
        for key, value in ticket_details.items():
            st.write(f"**{key}:** {value}")

        # Display message section
        message_section(selected_ticket)

    # Map view in the bottom section
    with bottom:
        st.header("Map View")
        map_ = plot_map(data)
        st_folium(map_)

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

            # Display message section
            message_section(ticket_number)
        else:
            st.warning("Ticket not found.")
