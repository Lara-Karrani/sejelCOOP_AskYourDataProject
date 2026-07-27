#Results Page
#TF
import streamlit as st

st.set_page_config(
    page_title="Results",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Results")

#User Question
question = st.session_state.get("question", "")
outputs = st.session_state.get("outputs", [])

st.subheader("Your Question")
st.info(question)

st.divider()

#Tables
st.subheader("📋Results")

#Backend display the results table here
st.info("Results table will appear here.")

st.divider()

#Chart Results
if "chart" in outputs:

    st.subheader("📊Chart")

    #Backend display the chart here
    st.info("Chart will appear here.")

    st.divider()


#Summary Results
if "summary" in outputs:

    st.subheader("📝Results Explanation")

    #Backend display the AI summary here
    st.info("Summary will appear here.")

    st.divider()


#SQL Query Results
if "sql" in outputs:

    st.subheader("💻SQL Query")

    #Backend display the SQL query here
    st.code(
        "-- SQL query will appear here",
        language="sql"
    )

    st.divider()


#Ask Another Question Button
if st.button("⬅️Ask Another Question"):
    st.switch_page("pages/Ask.py")
#TF