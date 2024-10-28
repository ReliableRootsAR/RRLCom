import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# URLs for Open and Closed Tickets Sheets
open_tickets_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqXBuQtvBF0Y/export?format=csv"
closed_tickets_url = "https://docs.google.com/spreadsheets/d/1Sa7qXR2oWtvYf9n1NRrSoI6EFWp31s7hqXBuQtvBF0Y/export?format=csv"

# Initialize message storage in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

@st.cache_data
def load_data():
    """Load open and closed tickets from Google Sheets."""
    try:
        open_tickets = pd.read_csv(open_tickets_url)
        closed_tickets = pd.read_csv(closed_tickets_url)

        # Clean ticket numbers
        open_tickets["RequestNum"] = open_tickets["RequestNum"].astype(str).str.replace(",", "")
        closed_tickets["RequestNum"] = closed_tickets["RequestNum"].astype(str).str.replace(",", "")

        return open_tickets, closed_tickets
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

open_tickets, closed_tickets = load_data()

def plot_tickets_on_map(tickets):
    """Plot tickets on a map."""
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

def send_message(ticket_num, sender, message, attachments):
    """Send a new message or reply."""
    st.session_state["messages"].append({
        "ticket_num": ticket_num,
        "sender": sender,
        "message": message,
        "attachments": attachments,
        "status": "Open"
    })

def view_messages(ticket_num):
    """View all messages for a specific ticket."""
    messages = [msg for msg in st.session_state["messages"] if msg["ticket_num"] == ticket_num]

    if not messages:
        st.write("No messages for this ticket yet.")
        return

    for msg in messages:
        st.write(f"**{msg['sender']}**: {msg['message']} ({msg['status']})")
        if msg["attachments"]:
            for attachment in msg["attachments"]:
                st.write(f"📎 {attachment.name}")
        st.write("---")

def ticket_dashboard(tickets, role, key_prefix):
    """Display ticket dashboard with search, list, and map views."""
    search_term = st.text_input("Search by Contractor, Ticket Number, or Date", key=f"{key_prefix}_search")
    filtered_tickets = tickets[tickets.apply(lambda row: search_term.lower() in str(row.values).lower(), axis=1)]

    tab1, tab2 = st.tabs(["List View", "Map View"])

    with tab1:
        st.dataframe(filtered_tickets)

        ticket_num = st.text_input("Enter Ticket Number to View Messages", key=f"{key_prefix}_ticket_num")
        if ticket_num:
            view_messages(ticket_num)

            message = st.text_area("New Message", key=f"{key_prefix}_message")
            attachments = st.file_uploader("Attach Files", accept_multiple_files=True, key=f"{key_prefix}_attachments")

            if st.button("Send Message", key=f"{key_prefix}_send_message"):
                send_message(ticket_num, role, message, attachments)
                st.success("Message sent!")

    with tab2:
        map_view = plot_tickets_on_map(filtered_tickets)
        folium_static(map_view, width=800, height=400)

def admin_dashboard():
    """Admin dashboard with open and closed tickets."""
    st.title("Admin Dashboard")

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        ticket_dashboard(open_tickets, "Admin", "admin_open")

    with tab2:
        ticket_dashboard(closed_tickets, "Admin", "admin_closed")

def locator_dashboard(username):
    """Locator dashboard for assigned tickets."""
    st.title(f"Locator Dashboard - {username}")

    locator_open = open_tickets[open_tickets["Assigned Name"] == username]
    locator_closed = closed_tickets[closed_tickets["Completed By"] == username]

    tab1, tab2 = st.tabs(["Open Tickets", "Closed Tickets"])

    with tab1:
        ticket_dashboard(locator_open, "Locator", f"locator_open_{username}")

    with tab2:
        ticket_dashboard(locator_closed, "Locator", f"locator_closed_{username}")

def logout():
    """Logout function to clear session state."""
    st.session_state.clear()
    st.session_state["logged_out"] = True

def login():
    """User login interface."""
    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if username == "admin" and password == "admin123":
            st.session_state["role"] = "Admin"
        elif username in open_tickets["Assigned Name"].unique():
            st.session_state["role"] = "Locator"
            st.session_state["username"] = username
        else:
            st.error("Invalid credentials")

    if "role" in st.session_state:
        st.sidebar.button("Logout", on_click=logout, key="sidebar_logout")

if "role" not in st.session_state or st.session_state.get("logged_out", False):
    if "logged_out" in st.session_state:
        del st.session_state["logged_out"]
    login()
else:
    role = st.session_state["role"]
    username = st.session_state.get("username", "")

    st.sidebar.button("Logout", on_click=logout, key="main_logout")

    if role == "Admin":
        admin_dashboard()
    elif role == "Locator":
        locator_dashboard(username)
