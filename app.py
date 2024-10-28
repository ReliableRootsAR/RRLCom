import streamlit as st

st.title("RRLCom - Locator & Contractor Communication App")
st.write("Welcome to the communication platform for Reliable Roots Locating!")

# Basic ticket submission form
name = st.text_input("Your Name")
message = st.text_area("Message")

if st.button("Send"):
    st.success(f"Message from {name} submitted!")
