# ----------------------------------------------------------------------------
# Streamlit page
# ----------------------------------------------------------------------------
#TF
import streamlit as st
 
import backend
 
st.set_page_config(
    page_title="AYD | Ask Your Data",
    page_icon="assets/icons/bus.svg",
    layout="wide"
)
 
#Logo
st.logo("assets/logo.svg")
 
#Home page
left, center, right = st.columns([1.1, 2.2, 1.3], vertical_alignment="center")
 
with left:
    st.image("assets/logo.svg", width=170)
 
with center:
    st.markdown(
        """
        # Ask Your Data
        """
    )
 
    st.markdown(
        """
        Explore transportation companies, buses, drivers, and tickets
        by asking questions in plain English with no SQL knowledge required.
        """
    )
 
    st.write("")
 
    if st.button(
        "Start Asking Questions",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/Ask.py")
 
with right:
    st.image("assets/bus2.svg", width=360)
 
#Cards
 
icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")
with icon:
    st.image("assets/icons/chart-no-axes-combined.svg", width=30)
with title:
    st.subheader("Database Overview")
 
bus_card, driver_card, ticket_card, company_card = st.columns(4)
 
with bus_card:
    with st.container(border=True):
 
        st.image("assets/icons/bus.svg", width=35)
 
        st.metric(
            "Total Buses",
            backend.get_total_buses()
        )
 
        st.caption("Total buses in system")
 
with driver_card:
    with st.container(border=True):
 
        st.image("assets/icons/user.svg", width=35)
 
        st.metric(
            "Total Drivers",
            backend.get_total_drivers()
        )
 
        st.caption("Total drivers in system")
 
with ticket_card:
    with st.container(border=True):
 
        st.image("assets/icons/ticket.svg", width=35)
 
        st.metric(
            "Total Tickets",
            backend.get_total_tickets()
        )
 
        st.caption("Total tickets in system")
 
with company_card:
    with st.container(border=True):
 
        st.image("assets/icons/building.svg", width=35)
 
        st.metric(
            "Total Companies",
            backend.get_total_companies()
        )
 
        st.caption("Total companies in system")
 
st.divider()
 
icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")
with icon:
    st.image("assets/icons/rocket.svg", width=30)
with title:
    st.subheader("Start Exploring")
 
st.caption("Here are some ideas to get you started.")
 
q1, q2, q3, q4 = st.columns(4)
 
with q1:
    with st.container(border=True):
        st.image("assets/icons/building.svg", width=35)
        st.markdown("**Which company has the largest fleet?**")
        st.caption("Explore company fleet statistics.")
 
        if st.button(
            "Ask →",
            use_container_width=True,
            type="primary",
            key="fleet",
        ):
            st.session_state.default_question = (
                "Which company has the largest fleet?"
            )
            st.switch_page("pages/Ask.py")
 
with q2:
    with st.container(border=True):
        st.image("assets/icons/bus.svg", width=35)
        st.markdown("**Show me buses by bus type**")
        st.caption("View buses grouped by their type.")
 
        if st.button(
            "Ask →",
            type="primary",
            use_container_width=True,
            key="bus_type",
        ):
            st.session_state.default_question = (
                "Show me buses by bus type."
            )
            st.switch_page("pages/Ask.py")
 
with q3:
    with st.container(border=True):
        st.image("assets/icons/user.svg", width=35)
        st.markdown("**List active drivers in Makkah**")
        st.caption("Display all active drivers in Makkah.")
 
        if st.button(
            "Ask →",
            use_container_width=True,
            type="primary",
            key="drivers",
        ):
            st.session_state.default_question = (
                "List active drivers in Makkah."
            )
            st.switch_page("pages/Ask.py")
 
with q4:
    with st.container(border=True):
        st.image("assets/icons/ticket.svg", width=35)
        st.markdown("**How many tickets were issued last month?**")
        st.caption("View monthly ticket statistics.")
 
        if st.button(
            "Ask →",
            type="primary",
            use_container_width=True,
            key="tickets",
        ):
            st.session_state.default_question = (
                "How many tickets were issued last month?"
            )
            st.switch_page("pages/Ask.py")
 
 
icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")
with icon:
    st.image("assets/icons/sparkles.svg", width=30)
with title:
    st.subheader("Why Choose AYD?")
 
feature1, feature2, feature3, feature4 = st.columns(4)
 
with feature1:
    with st.container(border=True):
        st.image("assets/icons/message-circle.svg", width=35)
        st.markdown("**Ask in Plain English**")
        st.caption(
            "No SQL knowledge needed. Just ask naturally."
        )
 
with feature2:
    with st.container(border=True):
        st.image("assets/icons/shield-check.svg", width=35)
        st.markdown("**Smart & Safe**")
        st.caption(
            "AI generates safe SQL queries for your data."
        )
 
with feature3:
    with st.container(border=True):
        st.image("assets/icons/chart-no-axes-combined.svg", width=35)
        st.markdown("**Visual Insights**")
        st.caption(
            "View your results as tables and charts."
        )
 
with feature4:
    with st.container(border=True):
        st.image("assets/icons/zap.svg", width=35)
        st.markdown("**Fast & Accurate**")
        st.caption(
            "Instant answers from your transportation database."
        )
#TF
 