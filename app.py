import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# URLs for Open and Closed Tickets Sheets
open_tickets_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqZXXI_jWbUVc/export?format=csv"
closed_tickets_url = "https://docs.google.com/spreadsheets/d/1Sa7qXR2oWtvYf9n1NRrSoI6EFWp31s7hqXBuQtvBF0Y/export?format=csv"

# Cache the data to improve performance
@st.cache_data
def load_data():
    """Load open and closed tickets from Google Sheets."""
    try:
        open_tickets = pd.read_csv(open_tickets_url)
        closed_tickets = pd.read_csv(closed_tickets_url)

        # Ensure ticket numbers are strings without commas
        open_tickets["RequestNum"] = open_tickets["RequestNum"].astype(str).str.replace(",", "")
        closed_tickets["RequestNum"] = closed_tickets["RequestNum"].astype(str).str.replace(",", "")

        return open_tickets, closed_tickets
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Load the data
open_tickets, closed_tickets = load_data()

# Plot tickets on a map
def plot_tickets_on_map(tickets):
    """Plot all relevant tickets on a map."""
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

# Admin Dashboard with Open and Closed Tabs (List and Map Views)
def admin_dashboard():
    st.title("Admin Dashboard")

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.subheader("Open Tickets - List View")
            st.dataframe(open_tickets)

        with subtabs[1]:
            st.subheader("Open Tickets - Map View")
            open_map = plot_tickets_on_map(open_tickets)
            folium_static(open_map, width=800, height=400)

    with tab2:
        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.subheader("Closed Tickets - List View")
            st.dataframe(closed_tickets)

        with subtabs[1]:
            st.subheader("Closed Tickets - Map View")
            closed_map = plot_tickets_on_map(closed_tickets)
            folium_static(closed_map, width=800, height=400)

# Locator Dashboard with Open and Closed Tabs (List and Map Views)
def locator_dashboard(username):
    st.title(f"Locator Dashboard - {username}")

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.subheader("Open Tickets Assigned to You - List View")
            locator_open_tickets = open_tickets[open_tickets["Assigned Name"] == username]
            st.dataframe(locator_open_tickets)

        with subtabs[1]:
            st.subheader("Open Tickets Assigned to You - Map View")
            open_map = plot_tickets_on_map(locator_open_tickets)
            folium_static(open_map, width=800, height=400)

    with tab2:
        subtabs = st.tabs(["List View", "Map View"])

        with subtabs[0]:
            st.subheader("Closed Tickets Completed by You - List View")
            locator_closed_tickets = closed_tickets[closed_tickets["Completed By"] == username]
            st.dataframe(locator_closed_tickets)

        with subtabs[1]:
            st.subheader("Closed Tickets Completed by You - Map View")
            closed_map = plot_tickets_on_map(locator_closed_tickets)
            folium_static(closed_map, width=800, height=400)

# Contractor Dashboard
def contractor_dashboard(username):
    contractor_tickets = open_tickets[open_tickets["Excavator"] == username]
    st.title(f"Contractor Dashboard - {username}")
    st.dataframe(contractor_tickets)

# Logout Functionality
def logout():
    """Clear session state and set logout flag."""
    st.session_state.clear()
    st.session_state["logged_out"] = True

# Login Page
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

# Main App Flow
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
