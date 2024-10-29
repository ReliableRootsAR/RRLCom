import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# URLs for Open and Closed Tickets Sheets
open_tickets_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqZXXI_jWbUVc/export?format=csv"
closed_tickets_url = "https://docs.google.com/spreadsheets/d/1Sa7qXR2oWtvYf9n1NRrSoI6EFWp31s7hqXBuQtvBF0Y/export?format=csv"

@st.cache_data
def load_data():
    """Load open and closed tickets from Google Sheets."""
    try:
        open_tickets = pd.read_csv(open_tickets_url)
        closed_tickets = pd.read_csv(closed_tickets_url)

        open_tickets["RequestNum"] = open_tickets["RequestNum"].astype(str).str.replace(",", "")
        closed_tickets["RequestNum"] = closed_tickets["RequestNum"].astype(str).str.replace(",", "")

        return open_tickets, closed_tickets
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

open_tickets, closed_tickets = load_data()

# Placeholder data for messages
data = {
    "TicketNum": ["1234", "5678"],
    "Messages": [
        [{"author": "admin", "content": "Message 1", "status": "Open"}],
        [{"author": "locator", "content": "Message 2", "status": "Open"}]
    ]
}
messages_df = pd.DataFrame(data)

def plot_tickets_on_map(tickets):
    """Plot filtered tickets on a map."""
    m = folium.Map(location=[38.9717, -95.2353], zoom_start=12)
    for _, ticket in tickets.iterrows():
        try:
            latitude = float(ticket.get("Latitude", 0))
            longitude = float(ticket.get("Longitude", 0))
            address = ticket.get("Address", "Not Available")
            request_num = ticket.get("RequestNum", "Unknown")
            excavator = ticket.get("Excavator", "Unknown")
            status = ticket.get("Status", "Unknown")

            folium.Marker(
                location=[latitude, longitude],
                popup=(
                    f"<b>RequestNum:</b> {request_num}<br>"
                    f"<b>Address:</b> {address}<br>"
                    f"<b>Excavator:</b> {excavator}<br>"
                    f"<b>Status:</b> {status}"
                ),
                tooltip=request_num
            ).add_to(m)
        except ValueError:
            st.warning("Skipping ticket with invalid coordinates.")
    return m

def search_tickets(tickets, date_column, start_date, end_date, contractor):
    """Filter tickets by the date column and contractor."""
    # Ensure consistent datetime format with UTC timezone
    tickets[date_column] = pd.to_datetime(tickets[date_column], errors='coerce').dt.tz_localize(None)

    # Drop rows with invalid dates (NaT)
    tickets = tickets.dropna(subset=[date_column])

    # Convert input dates to datetime format (no timezone)
    start_date = pd.to_datetime(start_date).replace(tzinfo=None)
    end_date = pd.to_datetime(end_date).replace(tzinfo=None)

    # Filter by date range
    if start_date and end_date:
        tickets = tickets[
            (tickets[date_column] >= start_date) &
            (tickets[date_column] <= end_date)
        ]

    # Filter by contractor name if provided
    if contractor:
        tickets = tickets[tickets["Excavator"].str.contains(contractor, case=False, na=False)]

    return tickets

def admin_dashboard():
    st.title("Admin Dashboard")

    # Sidebar with logout
    st.sidebar.header("Admin Menu")
    st.sidebar.button("Logout", on_click=logout, key="admin_logout")

    # Tabs for open and closed tickets
    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        st.subheader("Open Tickets")
        start_date = st.date_input("Start Date", key="admin_open_start")
        end_date = st.date_input("End Date", key="admin_open_end")
        contractor = st.text_input("Contractor Name", key="admin_open_contractor")

        filtered_open_tickets = search_tickets(open_tickets, "Work to Begin Date", start_date, end_date, contractor)
        st.subheader(f"Total Open Tickets: {len(filtered_open_tickets)}")

        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.dataframe(filtered_open_tickets)

        with subtabs[1]:
            open_map = plot_tickets_on_map(filtered_open_tickets)
            folium_static(open_map, width=800, height=400)

    with tab2:
        st.subheader("Closed Tickets")
        start_date = st.date_input("Start Date", key="admin_closed_start")
        end_date = st.date_input("End Date", key="admin_closed_end")
        contractor = st.text_input("Contractor Name", key="admin_closed_contractor")

        filtered_closed_tickets = search_tickets(closed_tickets, "Date Completed", start_date, end_date, contractor)
        st.subheader(f"Total Closed Tickets: {len(filtered_closed_tickets)}")

        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.dataframe(filtered_closed_tickets)

        with subtabs[1]:
            closed_map = plot_tickets_on_map(filtered_closed_tickets)
            folium_static(closed_map, width=800, height=400)

def locator_dashboard(username):
    st.title(f"Locator Dashboard - {username}")

    st.sidebar.header("Locator Menu")
    st.sidebar.button("Logout", on_click=logout, key="locator_logout")

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        st.subheader("Open Tickets")
        start_date = st.date_input("Start Date", key="locator_open_start")
        end_date = st.date_input("End Date", key="locator_open_end")
        contractor = st.text_input("Contractor Name", key="locator_open_contractor")

        locator_open_tickets = open_tickets[open_tickets["Assigned Name"] == username]
        filtered_open_tickets = search_tickets(locator_open_tickets, "Work to Begin Date", start_date, end_date, contractor)
        st.subheader(f"Total Open Tickets: {len(filtered_open_tickets)}")

        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.dataframe(filtered_open_tickets)

        with subtabs[1]:
            open_map = plot_tickets_on_map(filtered_open_tickets)
            folium_static(open_map, width=800, height=400)

    with tab2:
        st.subheader("Closed Tickets")
        start_date = st.date_input("Start Date", key="locator_closed_start")
        end_date = st.date_input("End Date", key="locator_closed_end")
        contractor = st.text_input("Contractor Name", key="locator_closed_contractor")

        locator_closed_tickets = closed_tickets[closed_tickets["Completed By"] == username]
        filtered_closed_tickets = search_tickets(locator_closed_tickets, "Date Completed", start_date, end_date, contractor)
        st.subheader(f"Total Closed Tickets: {len(filtered_closed_tickets)}")

        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.dataframe(filtered_closed_tickets)

        with subtabs[1]:
            closed_map = plot_tickets_on_map(filtered_closed_tickets)
            folium_static(closed_map, width=800, height=400)

def messages_dashboard(username):
    st.title(f"Messages Dashboard - {username}")

    st.sidebar.header("Messages Menu")
    st.sidebar.button("Logout", on_click=logout, key="messages_logout")

    tab1, tab2 = st.tabs(["Open Messages", "Closed Messages"])

    with tab1:
        st.subheader("Open Messages")
        open_messages = messages_df[messages_df['Messages'].apply(lambda x: any(msg['status'] == 'Open' for msg in x))]
        st.dataframe(open_messages)
