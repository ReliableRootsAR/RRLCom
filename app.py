import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# URLs for Open and Closed Tickets Sheets
open_tickets_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqXXXI_jWbUVc/export?format=csv"
closed_tickets_url = "https://docs.google.com/spreadsheets/d/1Sa7qXR2oWtvYf9n1NRrSoI6EFWp31s7hqXBuQtvBF0Y/export?format=csv"

# Initialize message storage in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

@st.cache_data
def load_data():
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

def send_message(ticket_num, sender, message, attachments):
    """Add a message with attachments to session state."""
    st.session_state["messages"].append({
        "ticket_num": ticket_num,
        "sender": sender,
        "message": message,
        "attachments": attachments,
        "status": "Open"
    })

def view_messages(ticket_num=None, status_filter=None):
    """Display messages with collapsible sections."""
    messages = st.session_state["messages"]

    if status_filter:
        messages = [msg for msg in messages if msg["status"] == status_filter]

    grouped_messages = {}
    for msg in messages:
        ticket = msg["ticket_num"]
        if ticket not in grouped_messages:
            grouped_messages[ticket] = []
        grouped_messages[ticket].append(msg)

    for ticket, msgs in grouped_messages.items():
        with st.expander(f"Ticket {ticket} - {len(msgs)} message(s)"):
            for msg in msgs:
                st.write(f"**{msg['sender']}**: {msg['message']} ({msg['status']})")
                if msg["attachments"]:
                    for attachment in msg["attachments"]:
                        st.write(f"📎 {attachment.name}")
                st.write("---")

            # Reply box and Close Message button
            reply = st.text_area(f"Reply to Ticket {ticket}", key=f"reply_{ticket}")
            attachments = st.file_uploader(
                f"Attach files to Ticket {ticket}",
                accept_multiple_files=True,
                key=f"attach_{ticket}"
            )
            if st.button(f"Send Reply for Ticket {ticket}", key=f"send_reply_{ticket}"):
                send_message(ticket, "Reply", reply, attachments)
                st.success("Reply sent!")

            if st.button(f"Close Ticket {ticket}", key=f"close_{ticket}"):
                for msg in msgs:
                    msg["status"] = "Closed"
                st.success(f"Ticket {ticket} closed.")

def message_dashboard():
    """Dedicated dashboard for viewing open and closed messages."""
    st.title("Messages")

    tab1, tab2 = st.tabs(["Open Messages", "Closed Messages"])

    with tab1:
        st.subheader("Open Messages")
        view_messages(status_filter="Open")

    with tab2:
        st.subheader("Closed Messages")
        view_messages(status_filter="Closed")

def logout():
    """Clear session state and log out."""
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
        message_dashboard()
    elif role == "Locator":
        message_dashboard()
