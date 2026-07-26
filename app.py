"""
PROJECT A -- "Ask your data" chatbot
=====================================
Type a question in plain English. The app asks Claude to write a SQL query,
checks that the query is safe, runs it against the sample transportation
database, and shows both the answer and the SQL that produced it.

HOW TO RUN
  1. python create_database.py
     (only needed once -- creates transport.db)

  2. streamlit run app.py
"""

import re
import sqlite3

import pandas as pd
import streamlit as st
from anthropic import Anthropic


DB_FILE = "transport.db"

# The API key is read from Streamlit secrets so it never lives in the code.
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def get_schema_text():
    """Return a plain-text description of the database tables and columns."""

    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)

    try:
        tables = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        lines = []

        for (table_name,) in tables:
            columns = conn.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            column_names = ", ".join(column[1] for column in columns)
            lines.append(f"{table_name}({column_names})")

        return "\n".join(lines)

    finally:
        conn.close()


def generate_sql(question, schema):
    """Ask Claude to turn a plain-English question into one SQLite query."""

    prompt = f"""
You are an expert SQLite data analyst.

The database contains FAKE sample data about Hajj and Umrah transportation
companies, buses, drivers, and tickets.

Database schema:
{schema}

User question:
{question}

Write exactly one SQLite query that answers the user's question.

Rules:
- Return ONLY the SQL query.
- Do not include explanations.
- Do not include Markdown or backticks.
- The query must be a read-only SELECT statement.
- Use only the tables and columns shown in the schema.
- Never invent table names or column names.
- Use JOINs when information is needed from multiple tables.
- Use SQLite-compatible syntax only.
- Use clear column aliases.
- Use COUNT(DISTINCT ...) when duplicate rows could affect a count.
- For questions about companies, include company_name when useful.
- For status questions, use the exact text values stored in the database.
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    sql = response.content[0].text.strip()

    # Remove Markdown code fences if the model adds them.
    if sql.startswith("```"):
        sql = sql.strip("`").strip()

        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()

    return sql.strip()


def is_safe(sql):
    """Return True only for one harmless read-only SELECT query."""

    cleaned = sql.strip()

    if not cleaned:
        return False

    lowered = cleaned.lower()

    # Only SELECT queries are allowed.
    if not re.match(r"^\s*select\b", lowered):
        return False

    dangerous_keywords = [
        "drop",
        "delete",
        "update",
        "insert",
        "alter",
        "create",
        "replace",
        "truncate",
        "attach",
        "detach",
        "pragma",
        "vacuum",
        "reindex",
    ]

    for keyword in dangerous_keywords:
        if re.search(rf"\b{keyword}\b", lowered):
            return False

    # Allow one optional semicolon only at the very end.
    without_final_semicolon = cleaned.rstrip().rstrip(";").strip()

    if ";" in without_final_semicolon:
        return False

    return True


def run_query(sql):
    """Run the safe SELECT query and return the result as a DataFrame."""

    # Read-only mode adds another layer of protection.
    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)

    try:
        return pd.read_sql_query(sql, conn)

    finally:
        conn.close()


def can_draw_bar_chart(results):
    """Check whether the result has one label column and one numeric column."""

    if results.empty or len(results.columns) != 2:
        return False

    first_column = results.columns[0]
    second_column = results.columns[1]

    first_is_text = (
        pd.api.types.is_object_dtype(results[first_column])
        or pd.api.types.is_string_dtype(results[first_column])
    )

    second_is_number = pd.api.types.is_numeric_dtype(results[second_column])

    return first_is_text and second_is_number


# ----------------------------------------------------------------------------
# Streamlit page
# ----------------------------------------------------------------------------

st.set_page_config(
    page_title="Ask Your Transportation Data",
    page_icon="🚌",
    layout="wide",
)

st.title("🚌 Ask your transportation data")

st.caption(
    "Ask questions about the fake Hajj and Umrah transportation database "
    "in plain English."
)

try:
    schema = get_schema_text()

except sqlite3.Error:
    st.error(
        "transport.db was not found. Run `python create_database.py` first."
    )
    st.stop()


with st.expander("What can I ask about?"):
    st.write(
        "The database contains transportation companies, buses, drivers, "
        "and tickets."
    )
    st.code(schema)

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


question = st.text_input(
    "Your question",
    placeholder="e.g. Which company has the most active buses?",
)


if st.button("Ask", type="primary") and question.strip():
    try:
        with st.spinner("Thinking..."):
            sql = generate_sql(question.strip(), schema)

        st.subheader("The SQL query")
        st.code(sql, language="sql")

        if not is_safe(sql):
            st.error(
                "The query was blocked because it was not a safe, "
                "read-only SELECT query."
            )

        else:
            results = run_query(sql)

            st.subheader("Answer")

            if results.empty:
                st.info("The query ran successfully, but no matching data was found.")

            else:
                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True,
                )

                if can_draw_bar_chart(results):
                    first_column = results.columns[0]
                    chart_data = results.set_index(first_column)

                    st.subheader("Chart")
                    st.bar_chart(chart_data)

    except Exception as error:
        st.error(f"The query did not run. Error: {error}")
        st.info(
            "Look at the SQL above. Claude may have used the wrong column "
            "or misunderstood the question."
        )