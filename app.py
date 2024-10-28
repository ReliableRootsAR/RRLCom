import streamlit as st
import pandas as pd

# Public Google Sheet URL (replace 'edit' with 'export?format=csv' to get CSV data)
sheet_url = "https://docs.google.com/spreadsheets/d/1a1YSAMCFsUJn-PBSKlcIiKgGjvZaz7hqZXXI_jWbUVc/export?format=csv"

# Load the data into a DataFrame
@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

data = load_data()

# Search for ticket details by ticket number
def get_ticket_details(ticket_number):
    ticket = data[data["Ticket Number"].astype(str) == ticket_number]
    if ticket.empty:
        return None
    return ticket.iloc[0].to_dict()

# Streamlit UI
st.title("RRLCom - Ticket Search")

ticket_number = st.text_input("Enter Ticket Number")
if st.button("Search Ticket"):
    ticket_details = get_ticket_details(ticket_number)
    if ticket_details:
        st.write(ticket_details)
    else:
        st.warning("Ticket not found.")
