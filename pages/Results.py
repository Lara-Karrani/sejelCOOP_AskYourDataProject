#Results Page
#TF
import streamlit as st
 
from backend import can_draw_bar_chart
 
 
st.set_page_config(
    page_title="Results",
    page_icon="📊",
    layout="wide",
)
 
st.title("📊 Results")
 
st.caption(
    "Review your query results, charts, explanation, and generated SQL."
)
 
st.divider()
 
# Read saved data from Ask.py
question = st.session_state.get("question", "")
outputs = st.session_state.get("outputs", [])
generated_sql = st.session_state.get("generated_sql", "")
results = st.session_state.get("results", None)
 
 
# Protect the page if opened before asking a question
if not question or results is None:
    st.warning("Please ask a question first.")
 
    if st.button("Go to Ask Page"):
        st.switch_page("pages/Ask.py")
 
    st.stop()
 
 
# User Question
st.subheader("❓ Your Question")
st.info(question)
 
st.divider()
 
 
# Results Table
with st.container(border=True):
 
    st.subheader("📋 Query Results")
 
    if results.empty:
 
        st.warning(
            "No matching records were found."
        )
 
    else:
 
        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True,
        )
 
# Chart
if "chart" in outputs:
 
    with st.container(border=True):
 
        st.subheader("📊 Visualization")
 
        if can_draw_bar_chart(results):
 
            first_column = results.columns[0]
            second_column = results.columns[1]
 
            chart_data = results.set_index(first_column)[second_column]
 
            st.bar_chart(chart_data)
 
        else:
 
            st.info(
                "A bar chart cannot be created because the result must contain one text column and one numeric column."
            )
 
 
# Results Explanation
if "summary" in outputs:
 
    with st.container(border=True):
 
        st.subheader("📝 Results Explanation")
 
        if results.empty:
 
            st.info(
                "No matching records were found for this question."
            )
 
        elif len(results) == 1:
 
            st.info(
                f"The query returned 1 matching record with {len(results.columns)} result column(s)."
            )
 
        else:
 
            st.info(
                f"The query returned {len(results)} matching records with {len(results.columns)} result columns."
            )
 
 
# SQL Query
if "sql" in outputs:
    with st.container(border=True):
 
        st.subheader("💻 Generated SQL")
        st.code(
            generated_sql,
            language="sql",
        )
 
    st.divider()
 
 
# Ask Another Question
left, right = st.columns([5,1])
 
with right:
 
    if st.button(
        "⬅️ Ask Again",
        use_container_width=True,
    ):
        st.switch_page("pages/Ask.py")