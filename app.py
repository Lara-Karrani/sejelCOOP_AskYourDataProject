# ----------------------------------------------------------------------------
# Streamlit page
# ----------------------------------------------------------------------------
#TF
import streamlit as st
 
import backend
 
st.set_page_config(
    page_title="AYD | Ask Your Data",
    page_icon="🚌",
    layout="wide"
)
 
#Logo
st.logo("assets/logo.svg")

#Home page
col1, col2 = st.columns([0.5, 3])

with col1:
    st.image("assets/logo.svg", width=130) 

with col2:
    st.title("Ask Your Data")

st.caption(
    "Explore transportation companies, buses, drivers, and tickets by asking questions"
    "in plain English with no SQL knowledge required."
)
 
st.write("\n\n\n")
st.divider()
 
 
#Cards
 
st.subheader("📊 Database Overview")
 
bus_card, driver_card, ticket_card, company_card = st.columns(4)
 
with bus_card:
    st.metric(
        label="🚌 Total Buses",
        value=backend.get_total_buses()
    )
 
with driver_card:
    st.metric(
        label="👨 Drivers",
        value=backend.get_total_drivers()
    )
 
with ticket_card:
    st.metric(
        label="🎫 Tickets",
        value=backend.get_total_tickets()
    )
 
with company_card:
    st.metric(
        label="🏢 Companies",
        value=backend.get_total_companies()
    )
 
st.divider()
 
with st.container():
 
    st.subheader("🚀 Start Exploring")
 
    st.write(
        """
Ask questions about:
 
- Transportation companies
- Buses
- Drivers
- Tickets
 
The AI will generate SQL, execute it safely, and return the results.
"""
    )
 
    if st.button(
        "Start Asking",
        type="primary",
        use_container_width=True
    ):
        st.switch_page("pages/Ask.py")
 
st.divider()
 
st.subheader("💡 Popular Questions")
 
col1, col2 = st.columns(2)
 
with col1:
 
    if st.button(
        "🚌 Which company has the highest number of active buses?",
        use_container_width=True,
    ):
        st.session_state.default_question = (
            "Which company has the highest number of active buses?"
        )
        st.switch_page("pages/Ask.py")
 
    if st.button(
        "🔧 Show all buses currently under maintenance.",
        use_container_width=True,
    ):
        st.session_state.default_question = (
            "Show all buses currently under maintenance."
        )
        st.switch_page("pages/Ask.py")
 
    if st.button(
        "👨 Which company has the most drivers?",
        use_container_width=True,
    ):
        st.session_state.default_question = (
            "Which company has the most drivers?"
        )
        st.switch_page("pages/Ask.py")
 
with col2:
 
    if st.button(
        "🎫 How many tickets are there by status?",
        use_container_width=True,
    ):
        st.session_state.default_question = (
            "How many tickets are there by status?"
        )
        st.switch_page("pages/Ask.py")
 
    if st.button(
        "🏢 Show companies ordered by fleet size.",
        use_container_width=True,
    ):
        st.session_state.default_question = (
            "Show companies ordered by fleet size."
        )
        st.switch_page("pages/Ask.py")
 
    if st.button(
        "💺 What is the average number of seats per company?",
        use_container_width=True,
    ):
        st.session_state.default_question = (
            "What is the average number of seats per company?"
        )
        st.switch_page("pages/Ask.py")
 
 
#TF
 