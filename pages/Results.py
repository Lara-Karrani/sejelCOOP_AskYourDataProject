#Results Page
#TF
import streamlit as st
 
import backend
 
 
st.set_page_config(
    page_title="Results",
    page_icon="📊",
    layout="wide",
)
 
st.title("📊 Results")
 
st.caption(
    "Review your selected data output, visualisation, and generated SQL."
)
 
st.divider()
 
# Read saved data from Ask.py
question = st.session_state.get("question", "")
outputs = st.session_state.get("outputs", [])
generated_sql = st.session_state.get("generated_sql", "")
results = st.session_state.get("results", None)
related_sql = st.session_state.get("related_sql", "")
related_results = st.session_state.get("related_results", None)#LK
 
 
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
 # Summary
with st.container(border=True):

    st.subheader("📝 Summary")

    if related_results is None or related_results.empty:

        st.info(
            "No related summary data is available."
        )

    else:

        summary_parts = []

        for column in related_results.columns:

            value = related_results.iloc[0][column]

            clean_column = column.replace("_", " ").title()

            summary_parts.append(
                f"{clean_column}: {value}"
            )

        st.info(" | ".join(summary_parts))
        st.subheader("Related SQL")
        st.code(related_sql, language="sql")
 
# Results Table 
if "table" in outputs:#LK

    with st.container(border=True):

        st.subheader("Query Results")

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
 
        if backend.can_draw_bar_chart(results):
 
            first_column = results.columns[0]
            second_column = results.columns[1]
 
            chart_data = results.set_index(first_column)[second_column]
 
            st.bar_chart(chart_data)
 
        else:
 
            st.info(
                "A bar chart cannot be created because the result must contain one text column and one numeric column."
            )
 
 #Results Explanation Removed

 
 
# SQL Query LK
if "sql" in outputs:
    with st.container(border=True):

        st.subheader("💻 Generated SQL")
        st.code(
            generated_sql,
            language="sql",
        )

        explanation = backend.explain_sql(generated_sql)

        st.subheader("📝 Query Explanation")
        st.write(explanation)

    st.divider()
 
 
# Ask Another Question
left, right = st.columns([5,1])
 
with right:
 
    if st.button(
        "⬅️ Ask Again",
        use_container_width=True,
    ):
        st.switch_page("pages/Ask.py")