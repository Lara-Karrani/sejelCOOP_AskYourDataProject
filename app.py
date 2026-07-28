# ----------------------------------------------------------------------------
# Streamlit page
# ----------------------------------------------------------------------------
 
import streamlit as st
 
import backend
 
st.set_page_config(
    page_title="Ask Your Transportation Data",
    page_icon="🚌",
    layout="wide",
)
 
#TF
 
#Home page
st.title("🚌 Ask your transportation data")
 
st.caption(
    "Explore transportation companies, buses, drivers, and tickets by asking questions"
    "in plain English with no SQL knowledge required."
)
 
st.write("\n\n\n")
 
 
#Cards
bus_card, driver_card, ticket_card, company_card = st.columns(4)
 
st.metric("🚌 Buses", backend.get_total_buses())
 
st.metric("👨‍✈️ Drivers", backend.get_total_drivers())
 
st.metric("🎫 Tickets", backend.get_total_tickets())
 
#st.metric("🏢 Companies", backend.get_total_companies())
 
st.divider()
 
if st.button("Start Asking"):
    st.switch_page("pages/Ask.py")
 
 
#TF
 
with st.expander("What can I ask about?"):
    st.write(
        "The database contains transportation companies, buses, drivers, "
        "and tickets."
    )
   
    st.markdown(
        """
Example questions:
 
- Which company has the most buses?
- How many active drivers does each company have?
- Show all buses under maintenance.
- How many tickets are there by status?
- Which company has the most open tickets?
- What is the average number of seats for each company?
- Show the number of companies by operation type.
"""
    )