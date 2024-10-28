import streamlit as st
import pandas as pd

# Public Google Sheet URL (export as CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqZXXI_jWbUVc/export?format=csv"

# Cache the data to improve performance
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

# Load the data from the Google Sheet
data = load_data()

# Function to search for ticket details by ticket number
def get_ticket_details(ticket_number):
    ticket = data[data["Ticket Number"].astype(str) == ticket_number]
    if ticket.empty:
        return None
    return ticket.iloc[0].to_dict()

# Streamlit App UI
st.title("RRLCom - Ticket Management System")

# Input field for Ticket Number search
ticket_number = st.text_input("Enter Ticket Number")

# Search for the ticket when button is clicked
if st.button("Search Ticket"):
    ticket_details = get_ticket_details(ticket_number)
    if ticket_details:
        st.write("### Ticket Details")
        for key, value in ticket_details.items():
            st.write(f"**{key}:** {value}")
    else:
        st.warning("Ticket not found.")
