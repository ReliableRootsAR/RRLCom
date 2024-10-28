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
        data = pd.read_csv(sheet_url, dtype={"RequestNum": str})  # Ensure RequestNum is a string
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Initialize session state to track the selected ticket
if "selected_ticket" not in st.session_state:
    st.session_state["selected_ticket"] = None

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
            request_num = ticket.get("RequestNum", "N/A")
            excavator = ticket.get("Excavator", "No excavator available")
            work_type = ticket.get("TypeOfWork", "No work type available")

            # Create popup content with a JS function to update session state
            popup_content = folium.Popup(
                f"<b>RequestNum:</b> {request_num}<br>"
                f"<b>Excavator:</b> {excavator}<br>"
                f"<b>Type of Work:</b> {work_type}<br>"
                f'<button onclick="window.location.href=\'?selected={request_num}\'">Select Ticket</button>',
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

# Update session state when a ticket is clicked in the list
def on_ticket_select(request_num):
    st.session_state["selected_ticket"] = request_num

# Streamlit App UI
st.title("RRLCom - Ticket Management System")

# Sidebar for navigation
st.sidebar.title("Navigation")
menu_option = st.sidebar.selectbox(
    "Select an option:",
    ["List View", "Map/List View", "Search Ticket", "Messages"]
)

if menu_option == "List View":
    # List View: Display all tickets in a scrollable table
    st.header("All Tickets")
    st.dataframe(data)

elif menu_option == "Map/List View":
    # Map/List View: Ticket List on top, Map on bottom
    st.header("Map/List View")

    # Top: Ticket List (Clickable)
    with st.container():
        st.subheader("Ticket List")
        for i, row in data.iterrows():
            if st.button(f"{row['RequestNum']} - {row['Excavator']}"):
                on_ticket_select(row["RequestNum"])

    # Get the selected ticket from session state
    selected_ticket = st.session_state.get("selected_ticket")

    # Bottom: Map of Tickets
    with st.container():
        st.subheader("Tickets Map")
        map_ = plot_all_tickets(data)
        folium_static(map_, width=800, height=400)

    # Message Section
    if selected_ticket:
        st.subheader(f"Send a Message for Ticket: {selected_ticket}")
        message = st.text_area("Enter your message:")
        attachments = st.file_uploader("Attach files:", accept_multiple_files=True)
        
        if st.button("Send Message"):
            st.success(f"Message sent for Ticket {selected_ticket}.")
            if attachments:
                for file in attachments:
                    st.write(f"Attached: {file.name}")

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
