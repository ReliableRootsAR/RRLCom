import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# URLs for Open and Closed Tickets Sheets (replace with your URLs)
open_tickets_url = "https://docs.google.com/spreadsheets/d/your_open_sheet_id/export?format=csv"
closed_tickets_url = "https://docs.google.com/spreadsheets/d/your_closed_sheet_id/export?format=csv"

# Cache the data to improve performance
@st.cache_data
def load_data():
    """Load open and closed tickets from Google Sheets."""
    try:
        open_tickets = pd.read_csv(open_tickets_url)
        closed_tickets = pd.read_csv(closed_tickets_url)

        # Display columns for debugging (Optional: remove this in production)
        st.write("Open Tickets Columns:", open_tickets.columns)
        st.write("Closed Tickets Columns:", closed_tickets.columns)

        return open_tickets, closed_tickets
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Load the data
open_tickets, closed_tickets = load_data()

# Filter tickets by user role
def get_locator_tickets(username):
    """Return tickets assigned to or completed by the locator."""
    assigned_tickets = open_tickets[open_tickets["Assigned Name"] == username] if "Assigned Name" in open_tickets.columns else pd.DataFrame()
    completed_tickets = closed_tickets[closed_tickets["Completed By"] == username] if "Completed By" in closed_tickets.columns else pd.DataFrame()
    return pd.concat([assigned_tickets, completed_tickets])

def get_contractor_tickets(username):
    """Return tickets for the contractor."""
    return open_tickets[open_tickets["Excavator"] == username] if "Excavator" in open_tickets.columns else pd.DataFrame()

# Plot ticket on a map
def plot_tickets_on_map(tickets):
    """Plot all relevant tickets on a map."""
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
    st.write("View all tickets and manage user access.")
    st.subheader("Open Tickets")
    st.dataframe(open_tickets)
    st.subheader("Closed Tickets")
    st.dataframe(closed_tickets)

# Locator Dashboard
def locator_dashboard(username):
    st.title(f"Locator Dashboard - {username}")
    locator_tickets = get_locator_tickets(username)
    st.write("Tickets assigned to or completed by you.")
    st.dataframe(locator_tickets)

# Contractor Dashboard
def contractor_dashboard(username):
    st.title(f"Contractor Dashboard - {username}")
    contractor_tickets = get_contractor_tickets(username)
    st.write("Tickets associated with your organization.")
    st.dataframe(contractor_tickets)

# Login Page
def login():
    st.title("Login")

    # Display available usernames for testing (Remove in production)
    st.write("### Available Usernames (For Testing)")
    st.write("Admins: admin")
    st.write("Locators:", open_tickets["Assigned Name"].unique() if "Assigned Name" in open_tickets.columns else [])
    st.write("Contractors:", open_tickets["Excavator"].unique() if "Excavator" in open_tickets.columns else [])

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

# Main App Flow
if "role" not in st.session_state:
    login()
else:
    role = st.session_state["role"]
    username = st.session_state.get("username", "")

    if role == "Admin":
        admin_dashboard()
    elif role == "Locator":
        locator_dashboard(username)
    elif role == "Contractor":
        contractor_dashboard(username)
