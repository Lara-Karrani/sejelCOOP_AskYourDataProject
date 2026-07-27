#Asking Page
#TF
import streamlit as st

st.title("🤖Ask Your Data")

#Question
question = st.text_input(
    "Ask your question here",
    placeholder="ex. Which company has the most active buses?"
)

st.subheader("Choose output types")

#Output Options
sql_checkbox, chart_checkbox, summary_checkbox = st.columns(3)

with sql_checkbox:
    sql = st.checkbox(
        "💻SQL Query\n\nReview the generated SQL query."
    )

with chart_checkbox:
    chart = st.checkbox(
        "📊Chart\n\nVisualize the results clearly."
    )

with summary_checkbox:
    summary = st.checkbox(
        "📝Results Explanation\n\nRead an AI-generated summary."
    )

#Save Selected Outputs
selected_outputs = []

if sql:
    selected_outputs.append("sql")
if chart:
    selected_outputs.append("chart")
if summary:
    selected_outputs.append("summary")

#Ask Button
if st.button("ASK", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    elif len(selected_outputs) == 0:
        st.warning("Please select at least one output type.")

    else:
        st.session_state.question = question
        st.session_state.outputs = selected_outputs
        st.switch_page("pages/Results.py")
#TF