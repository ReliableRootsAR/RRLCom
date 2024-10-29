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
            latitude = float(ticket["Latitude"])
            longitude = float(ticket["Longitude"])
            request_num = ticket["RequestNum"]

            folium.Marker(
                location=[latitude, longitude],
                popup=f"<b>RequestNum:</b> {request_num}",
                tooltip=request_num
            ).add_to(m)
        except ValueError:
            st.warning("Skipping ticket with invalid coordinates.")
    return m

def search_tickets(tickets, date_column, start_date, end_date):
    """Filter tickets by date range with consistent timezone handling."""
    try:
        # Ensure the date column is in datetime format and remove timezone
        tickets[date_column] = pd.to_datetime(tickets[date_column], errors='coerce').dt.tz_localize(None)

        # Drop rows with invalid dates (NaT)
        tickets = tickets.dropna(subset=[date_column])

        # Convert start and end dates to datetime and remove timezone
        start_date = pd.to_datetime(start_date).tz_localize(None)
        end_date = pd.to_datetime(end_date).tz_localize(None)

        # Apply date filtering
        return tickets[(tickets[date_column] >= start_date) & (tickets[date_column] <= end_date)]
    except Exception as e:
        st.error(f"Error filtering tickets: {e}")
        return pd.DataFrame()

def view_messages(status_filter=None):
    """Display real-time open and closed messages."""
    messages = st.session_state["messages"]
    if status_filter:
        messages = [msg for msg in messages if msg["status"] == status_filter]

    for msg in messages:
        with st.expander(f"Ticket {msg['ticket_num']} - {msg['status']}"):
            st.write(f"**{msg['sender']}**: {msg['message']}")
            if msg["attachments"]:
                for attachment in msg["attachments"]:
                    st.write(f"📎 {attachment.name}")
            # Reply Section
            reply = st.text_area(f"Reply to Ticket {msg['ticket_num']}", key=f"reply_{msg['ticket_num']}")
            reply_attachments = st.file_uploader("Attach Files", accept_multiple_files=True, key=f"reply_attach_{msg['ticket_num']}")
            if st.button(f"Send Reply for Ticket {msg['ticket_num']}"):
                if reply:
                    msg.setdefault("replies", []).append({
                        "sender": "Locator/Admin",
                        "message": reply,
                        "attachments": reply_attachments
                    })
                    st.success("Reply sent!")
                else:
                    st.warning("Reply cannot be empty.")
            if msg["attachments"]:
                for attachment in msg["attachments"]:
                    st.write(f"📎 {attachment.name}")
            if st.button(f"Close Message for Ticket {msg['ticket_num']}"):
                msg["status"] = "Closed"
                st.experimental_rerun()

def send_message(ticket_num, sender, message, attachments):
    """Send a new message."""
    st.session_state["messages"].append({
        "ticket_num": ticket_num,
        "sender": sender,
        "message": message,
        "attachments": attachments,
        "status": "Open",
        "replies": []
    })

def ticket_dashboard(tickets, role, key_prefix):
    """Display tickets with list, map view, and messaging."""
    start_date = st.date_input("Start Date", key=f"{key_prefix}_start")
    end_date = st.date_input("End Date", key=f"{key_prefix}_end")
    filtered_tickets = search_tickets(tickets, "Work to Begin Date", start_date, end_date)

    tab1, tab2 = st.tabs(["List View", "Map View"])

    with tab1:
        st.dataframe(filtered_tickets)

        ticket_num = st.text_input("Enter Ticket Number", key=f"{key_prefix}_ticket_num")
        if ticket_num:
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

    st.subheader("Messages")
    view_messages("Open")

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

    st.subheader("Messages")
    view_messages("Open")

def logout():
    """Clear session state for logout."""
    st.session_state.clear()
    st.session_state["logged_out"] = True

def login():
    """User login interface."""
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
    login()
else:
    role = st.session_state["role"]
    username = st.session_state.get("username", "")

    if role == "Admin":
        admin_dashboard()
    elif role == "Locator":
        locator_dashboard(username)
