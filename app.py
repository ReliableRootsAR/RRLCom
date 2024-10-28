import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# URLs for Open and Closed Tickets Sheets
open_tickets_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqZXXI_jWbUVc/export?format=csv"
closed_tickets_url = "https://docs.google.com/spreadsheets/d/1Sa7qXR2oWtvYf9n1NRrSoI6EFWp31s7hqXBuQtvBF0Y/export?format=csv"

# Initialize message storage
if "messages" not in st.session_state:
    st.session_state["messages"] = []

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
            request_num = ticket.get("RequestNum", "Unknown")

            folium.Marker(
                location=[latitude, longitude],
                popup=f"<b>RequestNum:</b> {request_num}",
                tooltip=request_num
            ).add_to(m)
        except ValueError:
            st.warning("Skipping ticket with invalid coordinates.")
    return m

def send_message(ticket_num, sender, message):
    """Add a message to the session state."""
    st.session_state["messages"].append({
        "ticket_num": ticket_num,
        "sender": sender,
        "message": message,
        "status": "Open"
    })

def view_messages(ticket_num):
    """Display messages for a specific ticket."""
    messages = [msg for msg in st.session_state["messages"] if msg["ticket_num"] == ticket_num]
    for msg in messages:
        st.write(f"**{msg['sender']}**: {msg['message']} ({msg['status']})")

def close_message(ticket_num):
    """Mark all messages for a ticket as closed."""
    for msg in st.session_state["messages"]:
        if msg["ticket_num"] == ticket_num:
            msg["status"] = "Closed"

def ticket_dashboard(tickets, role):
    """Generic dashboard for viewing tickets."""
    tab1, tab2 = st.tabs(["List View", "Map View"])

    with tab1:
        st.dataframe(tickets)

    with tab2:
        map_view = plot_tickets_on_map(tickets)
        folium_static(map_view, width=800, height=400)

    ticket_num = st.text_input("Enter Ticket Number to View Messages")
    if ticket_num:
        view_messages(ticket_num)

    if role == "Locator" or role == "Admin":
        st.text_area("Enter your message", key="message_text")
        if st.button("Send"):
            message = st.session_state["message_text"]
            send_message(ticket_num, role, message)
            st.success("Message sent!")

def admin_dashboard():
    st.title("Admin Dashboard")

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        st.subheader("Open Tickets")
        ticket_dashboard(open_tickets, "Admin")

    with tab2:
        st.subheader("Closed Tickets")
        ticket_dashboard(closed_tickets, "Admin")

def locator_dashboard(username):
    st.title(f"Locator Dashboard - {username}")

    locator_open = open_tickets[open_tickets["Assigned Name"] == username]
    locator_closed = closed_tickets[closed_tickets["Completed By"] == username]

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        st.subheader("Open Tickets")
        ticket_dashboard(locator_open, "Locator")

    with tab2:
        st.subheader("Closed Tickets")
        ticket_dashboard(locator_closed, "Locator")

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
