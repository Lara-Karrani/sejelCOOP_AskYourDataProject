#Results Page
#TF
import streamlit as st
import pandas as pd

#LF
from backend import decide_chart_type, render_chart
import backend


st.set_page_config(
    page_title="Results",
    page_icon="assets/icons/chart-no-axes-combined.svg",
    layout="wide",
)


# Page Title
icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")

with icon:
    st.image(
        "assets/icons/chart-no-axes-combined.svg",
        width=30
    )

with title:
    st.title("Results")


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

    if st.button(
        "Ask Page",
        icon=":material/arrow_back:"
    ):
        st.switch_page("pages/Ask.py")

    st.stop()



# User Question

icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")

with icon:
    st.image(
        "assets/icons/question.svg",
        width=25
    )

with title:
    st.subheader("Your Question")


st.info(question)

st.divider()



# Summary

with st.container(border=True):

    icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")

    with icon:
        st.image(
            "assets/icons/scroll-text.svg",
            width=25
        )

    with title:
        st.subheader("Summary")


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
                width="stretch",
                hide_index=True,
            )



# Chart 
#LF

if "chart" in outputs:

    with st.container(border=True):

        icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")

        with icon:
            st.image(
                "assets/icons/chart-no-axes-combined.svg",
                width=25
            )

        with title:
            st.subheader("Visualization")


        if results.empty:

            st.info("No data available to visualize.")

        else:

            numeric_columns = [
                col for col in results.columns
                if pd.api.types.is_numeric_dtype(results[col])
            ]

            text_columns = [
                col for col in results.columns
                if not pd.api.types.is_numeric_dtype(results[col])
            ]


            if not numeric_columns or not text_columns:

                st.info(
                    "A chart cannot be created because the result needs "
                    "at least one text column and one numeric column."
                )

            else:

                label_column = text_columns[0]
                value_column = numeric_columns[0]

                chart_df = results[[label_column, value_column]].copy()

                chart_type = decide_chart_type(
                    data_description=f"Query result for the question: '{question}'",
                    columns=[label_column, value_column]
                )

                render_chart(
                    chart_df,
                    chart_type,
                    title=""
                )



#Results Explanation Removed



# SQL Query LK

if "sql" in outputs:

    with st.container(border=True):

        icon, title = st.columns([0.03, 0.97], vertical_alignment="center", gap="small")

        with icon:
            st.image(
                "assets/icons/database-search.svg",
                width=25
            )

        with title:
            st.subheader("Generated SQL")


        st.code(
            generated_sql,
            language="sql",
        )

        explanation = backend.explain_sql(generated_sql)

        st.caption(explanation)


    st.divider()



# Ask Another Question

left, right = st.columns([5,1])


with right:

    if st.button(
        "Ask Again",
        icon=":material/refresh:",
        width="stretch",
    ):
        st.switch_page("pages/Ask.py")