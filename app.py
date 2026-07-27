"""
PROJECT A -- "Ask your data" chatbot
=====================================
Type a question in plain English. The app asks Claude to write a SQL query,
checks that the query is safe, runs it against the sample transportation
database, and shows both the answer and the SQL that produced it.

HOW TO RUN
  1. python create_askyourdata_database.py
     (only needed once -- creates askyourdata.db)

  2. streamlit run app.py
"""

import re
import sqlite3

import pandas as pd
import streamlit as st
from anthropic import Anthropic


DB_FILE = "askyourdata.db"

# The API key is read from Streamlit secrets so it never lives in the code.
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

"LK"
def get_schema_text():
    """
    Return a detailed description of the database:
    tables, columns, foreign keys, and sample values.
    """

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

        database_context = []

        for (table_name,) in tables:
            database_context.append(f"\nTABLE: {table_name}")

            # Read columns and their types
            columns = conn.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            database_context.append("COLUMNS:")

            for column in columns:
                column_name = column[1]
                column_type = column[2] or "UNKNOWN"
                is_primary_key = column[5] == 1

                description = f"- {column_name} {column_type}"

                if is_primary_key:
                    description += " PRIMARY KEY"

                database_context.append(description)

            # Read foreign-key relationships
            foreign_keys = conn.execute(
                f'PRAGMA foreign_key_list("{table_name}")'
            ).fetchall()

            if foreign_keys:
                database_context.append("RELATIONSHIPS:")

                for foreign_key in foreign_keys:
                    referenced_table = foreign_key[2]
                    local_column = foreign_key[3]
                    referenced_column = foreign_key[4]

                    database_context.append(
                        f"- {table_name}.{local_column} references "
                        f"{referenced_table}.{referenced_column}"
                    )

            # Read a few sample values from text columns
            text_columns = [
                column[1]
                for column in columns
                if "CHAR" in (column[2] or "").upper()
                or "TEXT" in (column[2] or "").upper()
            ]

            sample_lines = []

            for column_name in text_columns[:5]:
                try:
                    values = conn.execute(
                        f"""
                        SELECT DISTINCT "{column_name}"
                        FROM "{table_name}"
                        WHERE "{column_name}" IS NOT NULL
                          AND TRIM(CAST("{column_name}" AS TEXT)) != ''
                        LIMIT 5
                        """
                    ).fetchall()

                    clean_values = [
                        str(value[0])
                        for value in values
                        if value[0] is not None
                    ]

                    if clean_values:
                        sample_lines.append(
                            f"- {column_name}: {clean_values}"
                        )

                except sqlite3.Error:
                    pass

            if sample_lines:
                database_context.append("SAMPLE VALUES:")
                database_context.extend(sample_lines)

        return "\n".join(database_context)

    finally:
        conn.close()
"LK"
"LK"
def generate_sql(question, schema):
    """Ask Claude to turn a plain-English question into one SQLite query."""

    prompt = f"""
You are the SQL generation engine for an application called Ask Your Data.

Your job is to convert a user's plain-English question into exactly one
valid SQLite SELECT query.

<database_information>
{schema}
</database_information>

<user_question>
{question}
</user_question>

<important_rules>
1. Return only the SQL query.
2. Do not return explanations.
3. Do not use Markdown or code fences.
4. Generate exactly one read-only SELECT query.
5. Use only tables and columns listed in the database information.
6. Never invent a table, column, relationship, or value.
7. Use the sample values exactly as stored in the database.
8. Use JOIN conditions based on the listed relationships.
9. Use COUNT(DISTINCT column) when joins could create duplicate records.
10. Use SQLite-compatible syntax only.
11. Give output columns clear English aliases.
12. For questions containing "each company", group the results by company.
13. For "highest", "largest", or "most", sort descending and use LIMIT 1
    unless the user asks for multiple results.
14. For "lowest", "smallest", or "least", sort ascending and use LIMIT 1.
15. For detailed record questions, return useful identifying columns rather
    than SELECT * when possible.
16. If the requested information cannot be answered using the supplied
    schema, return:
    SELECT 'The requested information is not available in the database.'
    AS message;
</important_rules>

Generate the SQL query now.
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
        "askyourdata.db was not found. Run `python create_database.py` first."
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

if st.button("Test Claude"):
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            messages=[
                {
                    "role": "user",
                    "content": "Reply only: Connected",
                }
            ],
        )

        st.success(response.content[0].text)

    except Exception as error:
        st.error(f"Claude connection failed: {error}")



        