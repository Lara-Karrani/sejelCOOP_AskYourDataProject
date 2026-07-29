#Asking Page
#TF
import streamlit as st
import sqlite3
import backend
 
st.title("🤖Ask Your Data")
 
 
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
 
    sql_checkbox, chart_checkbox, table_checkbox = st.columns(3)#LK
 
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
 
    with table_checkbox:#LK
        table_option = st.checkbox(
            "📋 Results Table",
            help="Display the query results in a table."
        )
 
#Save Selected Outputs
selected_outputs = []
 
if sql:
    selected_outputs.append("sql")
if chart:
    selected_outputs.append("chart")
if summary:
    selected_outputs.append("summary")
 
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
                generated_sql = generate_sql(question, schema)
 
                if not backend.is_safe(generated_sql):
                    st.error("The generated query was rejected for safety.")
                    st.stop()
 
                
                results = backend.run_query(generated_sql)

                related_sql = backend.generate_related_sql(question,generated_sql,schema,)

                if not backend.is_safe(related_sql):
                    st.error("The related query was rejected for safety.")
                    st.stop()

                related_results = backend.run_query(related_sql)
                
                st.session_state.question = question
                st.session_state.outputs = selected_outputs
                st.session_state.generated_sql = generated_sql
                st.session_state.results = results
                st.session_state.related_sql = related_sql#LK
                st.session_state.related_results = related_results#LK
 
                st.switch_page("pages/Results.py")
 
        except sqlite3.Error as error:
            st.error(f"Database error: {error}")
 
        except Exception as error:
            st.error(f"Unable to generate the answer: {error}")
#LK