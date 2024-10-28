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
    try:
        open_tickets = pd.read_csv(open_tickets_url)
        closed_tickets = pd.read_csv(closed_tickets_url)

        open_tickets["Request Num"] = open_tickets["Request Num"].astype(str).str.replace(",", "")
        closed_tickets["Request Num"] = closed_tickets["Request Num"].astype(str).str.replace(",", "")

        return open_tickets, closed_tickets
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Load the data
open_tickets, closed_tickets = load_data()

# Plot tickets on a map
def plot_tickets_on_map(tickets):
    m = folium.Map(location=[38.9717, -95.2353], zoom_start=12)
    for _, ticket in tickets.iterrows():
        try:
            latitude = float(ticket["Latitude"])
            longitude = float(ticket["Longitude"])
            folium.Marker(
                location=[latitude, longitude],
                popup=(
                    f"<b>RequestNum:</b> {ticket['Request Num']}<br>"
                    f"<b>Address:</b> {ticket['Address']}<br>"
                    f"<b>Excavator:</b> {ticket['Excavator']}<br>"
                    f"<b>Status:</b> {ticket['Status']}"
                ),
                tooltip=ticket["Request Num"]
            ).add_to(m)
        except ValueError:
            st.warning(f"Skipping ticket with invalid coordinates.")
    return m

# Admin Dashboard
def admin_dashboard():
    st.title("Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["Ticket List", "Map View", "Search"])

    with tab1:
        st.subheader("All Tickets - List View")
        all_tickets = pd.concat([open_tickets, closed_tickets])
        st.dataframe(all_tickets)

    with tab2:
        st.subheader("Tickets Map")
        map_ = plot_tickets_on_map(open_tickets)
        folium_static(map_, width=800, height=600)

    with tab3:
        st.subheader("Search Tickets by Number")
        ticket_number = st.text_input("Enter Ticket Number")
        if st.button("Search"):
            result = all_tickets[all_tickets["Request Num"] == ticket_number.strip()]
            if not result.empty:
                st.write(result)
                map_ = plot_tickets_on_map(result)
                folium_static(map_, width=800, height=400)
            else:
                st.warning("Ticket not found.")

# Locator Dashboard
def locator_dashboard(username):
    locator_tickets = open_tickets[open_tickets["Assigned Name"] == username]
    completed_tickets = closed_tickets[closed_tickets["Completed By"] == username]
    st.title(f"Locator Dashboard - {username}")
    st.dataframe(pd.concat([locator_tickets, completed_tickets]))

# Contractor Dashboard
def contractor_dashboard(username):
    contractor_tickets = open_tickets[open_tickets["Excavator"] == username]
    st.title(f"Contractor Dashboard - {username}")
    st.dataframe(contractor_tickets)

# Logout Functionality
def logout():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun()

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
if "role" not in st.session_state:
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
