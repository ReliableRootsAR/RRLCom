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
    """Filter tickets based on the date column and contractor."""
    if date_column in tickets.columns:
        if start_date and end_date:
            tickets = tickets[
                (pd.to_datetime(tickets[date_column]) >= start_date) &
                (pd.to_datetime(tickets[date_column]) <= end_date)
            ]
    if contractor:
        tickets = tickets[tickets["Excavator"].str.contains(contractor, case=False, na=False)]
    return tickets

def admin_dashboard():
    st.title("Admin Dashboard")

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        contractor = st.text_input("Contractor Name")

        filtered_open_tickets = search_tickets(open_tickets, "Work to Begin Date", start_date, end_date, contractor)
        st.subheader(f"Total Open Tickets: {len(filtered_open_tickets)}")

        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.dataframe(filtered_open_tickets)

        with subtabs[1]:
            open_map = plot_tickets_on_map(filtered_open_tickets)
            folium_static(open_map, width=800, height=400)

    with tab2:
        start_date = st.date_input("Start Date", key="closed_start")
        end_date = st.date_input("End Date", key="closed_end")
        contractor = st.text_input("Contractor Name", key="closed_contractor")

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

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        contractor = st.text_input("Contractor Name")

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

def logout():
    st.session_state.clear()
    st.session_state["logged_out"] = True

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["role"] = "Admin"
        elif username in open_tickets["Assigned Name"].unique():
            st.session_state["role"] = "Locator"
            st.session_state["username"] = username
        elif username in open_tickets["Excavator"].unique():
            st.session_state["role"] = "Contractor"
            st.session_state["username"] = username
        else:
            st.error("Invalid credentials")

    if "role" in st.session_state:
        st.sidebar.button("Logout", on_click=logout)

if "role" not in st.session_state or st.session_state.get("logged_out", False):
    if "logged_out" in st.session_state:
        del st.session_state["logged_out"]
    login()
else:
    role = st.session_state["role"]
    username = st.session_state.get("username", "")

    st.sidebar.button("Logout", on_click=logout)

    if role == "Admin":
        admin_dashboard()
    elif role == "Locator":
        locator_dashboard(username)
    elif role == "Contractor":
        contractor_dashboard(username)
