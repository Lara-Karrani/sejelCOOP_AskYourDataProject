#Asking Page
#TF
import streamlit as st
import sqlite3
from backend import get_schema_text, generate_sql, is_safe, run_query
 
st.title("🤖Ask Your Data")
 
#LF
if "question_history" not in st.session_state:
    st.session_state.question_history = []
 
#Question
default_question = st.session_state.get("default_question", "")
 
with st.container(border=True):
 
    st.subheader("💬 Ask a Question")
 
    input_col, button_col = st.columns([6, 1])
 
    with input_col:
 
        question = st.text_input(
            "Question",
            value=default_question,
            placeholder="e.g. Which company has the most active buses?",
            label_visibility="collapsed",
        )
 
    with button_col:
 
        ask_clicked = st.button(
            "🚀 Ask",
            type="primary",
            use_container_width=True,
        )
 
with st.container(border=True):
 
    st.subheader("📤 Choose Output")
 
    st.caption(
        "Select one or more output formats for your answer."
    )
 
    sql_checkbox, chart_checkbox, summary_checkbox = st.columns(3)
 
    with sql_checkbox:
        sql = st.checkbox(
            "💻 SQL Query",
            help="Show the generated SQL statement."
        )
 
    with chart_checkbox:
        chart = st.checkbox(
            "📊 Chart",
            help="Display a chart whenever possible."
        )
 
    with summary_checkbox:
        summary = st.checkbox(
            "📝 Results Explanation",
            help="Show an AI-generated explanation."
        )
 
#Save Selected Outputs
selected_outputs = []
 
if sql:
    selected_outputs.append("sql")
if chart:
    selected_outputs.append("chart")
if summary:
    selected_outputs.append("summary")
#LF
if st.button("🗑️ Start New Conversation"):
    st.session_state.question_history = []
    st.rerun()
 
#TF
#Ask Button
if ask_clicked:
 
    if not question.strip():
        st.warning("Please enter a question.")
 
    elif len(selected_outputs) == 0:
        st.warning("Please select at least one output type.")
 
    else:
        try:
            with st.spinner("Generating and running your query..."):
 
                schema = get_schema_text() #LF
                generated_sql = generate_sql(question, schema, conversation_history=st.session_state.question_history)
 
                if not is_safe(generated_sql):
                    st.error("The generated query was rejected for safety.")
                    st.stop()
 
                results = run_query(generated_sql)
 
                st.session_state.question = question
                st.session_state.outputs = selected_outputs
                st.session_state.generated_sql = generated_sql
                st.session_state.results = results
 
                #LF
                st.session_state.question_history.append(question)
 
                st.switch_page("pages/Results.py")
 
        except sqlite3.Error as error:
            st.error(f"Database error: {error}")
 
        except Exception as error:
            st.error(f"Unable to generate the answer: {error}")
#LK