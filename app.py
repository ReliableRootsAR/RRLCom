import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Public Google Sheet URL (export as CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqZXXI_jWbUVc/export?format=csv"

# Cache the data to improve performance
@st.cache_data
def load_data():
    """Load the ticket data from the Google Sheet."""
    try:
        data = pd.read_csv(sheet_url, dtype={"RequestNum": str})  # Ensure RequestNum is string
        st.write("### Column Names", list(data.columns))  # Debugging: Display column names
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

            # Extract relevant ticket details
            request_num = ticket["RequestNum"]
            excavator = ticket.get("Excavator", "N/A")
            work_type = ticket.get("TypeOfWork", "N/A")

            # Create popup content
            popup_content = folium.Popup(
                f"<b>RequestNum:</b> {request_num}<br>"
                f"<b>Excavator:</b> {excavator}<br>"
                f"<b>Type of Work:</b> {work_type}",
                max_width=300
            )

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
    ["List View", "Map View", "Search Ticket", "Messages"]
)

if menu_option == "List View":
    # List View: Display all tickets in a scrollable table
    st.header("All Tickets")
    st.dataframe(data)  # Display the entire dataset

elif menu_option == "Map View":
    # Map View: Display all tickets on a map
    st.header("Tickets Map")
    map_ = plot_all_tickets(data)  # Plot all tickets
    folium_static(map_, width=800, height=600)

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

elif menu_option == "Messages":
    # View sent messages (Placeholder for now)
    st.header("Sent Messages")
    st.write("This section will display all sent messages.")
