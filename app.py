import streamlit as st

# Sidebar menu
st.sidebar.title("RRLCom Navigation")
option = st.sidebar.selectbox(
    "Select a section:",
    ["Home", "Submit Ticket", "View Tickets", "Messages"]
)

# Store submitted tickets in session state (temporary storage)
if "tickets" not in st.session_state:
    st.session_state["tickets"] = []

# Home Section
if option == "Home":
    st.title("RRLCom - Locator & Contractor Communication App")
    st.write("Welcome to the Reliable Roots Locating communication platform!")

# Submit Ticket Section
elif option == "Submit Ticket":
    st.title("Submit a New Ticket")
    contractor_name = st.text_input("Contractor Name")
    location = st.text_input("Location of Work")
    description = st.text_area("Description of Work")

    if st.button("Submit Ticket"):
        st.session_state["tickets"].append({
            "contractor": contractor_name,
            "location": location,
            "description": description
        })
        st.success("Ticket submitted successfully!")

# View Tickets Section
elif option == "View Tickets":
    st.title("View Submitted Tickets")
    if len(st.session_state["tickets"]) == 0:
        st.warning("No tickets submitted yet.")
    else:
        for i, ticket in enumerate(st.session_state["tickets"]):
            st.write(f"### Ticket {i + 1}")
            st.write(f"**Contractor:** {ticket['contractor']}")
            st.write(f"**Location:** {ticket['location']}")
            st.write(f"**Description:** {ticket['description']}")
            st.write("---")

# Messages Section
elif option == "Messages":
    st.title("Message Board")
    message = st.text_area("Enter your message")
    if st.button("Send Message"):
        st.success(f"Message sent: {message}")
