#Lk
import re
import sqlite3

import pandas as pd
import streamlit as st
from anthropic import Anthropic


DB_FILE = "askyourdata.db"
print("Backend loaded from:", __file__)
print("Database file:", DB_FILE)
# The API key is read from Streamlit secrets so it never lives in the code.
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])



#LK
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
#LK
#LK
def generate_sql(question, schema, conversation_history=False):
    """Ask Claude to turn a plain-English question into one S
    QLite query,
    taking into account previous questions in the conversation for refinement."""
 
    #LF
    history_text = ""
    if conversation_history:
        history_text = "\n<conversation_history>\n"
        for i, past_question in enumerate(conversation_history, 1):
            history_text += f"{i}. {past_question}\n"
        history_text += "</conversation_history>\n"
        
    prompt = f"""
You are the SQL generation engine for an application called Ask Your Data.

Your job is to convert a user's plain-English question into exactly one
valid SQLite SELECT query.

<database_information>
{schema}
</database_information>

{history_text}

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
#LF
9. When a JOIN could multiply row counts (e.g., one bus joined to many
   trips), use COUNT(DISTINCT primary_key_column) instead of COUNT(*)
   to avoid inflated totals.
10. Use SQLite-compatible syntax only.
11. Give output columns clear English aliases.
#LF
12. For questions containing "each X" (e.g., each company, each driver,
    each bus), group the results by X accordingly.
13. For "highest", "largest", or "most", sort descending and use LIMIT 1
    unless the user asks for multiple results.
14. For "lowest", "smallest", or "least", sort ascending and use LIMIT 1.
#LF
15. For detailed record questions:
    - If the question can be answered using a single table only (no JOIN
      required), SELECT * is allowed.
    - If the question requires a JOIN across multiple tables, return
      identifying columns (such as name, ID, or code fields) plus the
      specific attributes requested, rather than SELECT *, to avoid
      duplicated or excessive columns.
16. If the requested information cannot be answered using the supplied
    schema, return:
    SELECT 'The requested information is not available in the database.'
    AS message;
#LF
17. When the question refers to a time period (e.g., "this season",
    "last month", "in 2024"), filter using the relevant date column
    based on the schema. If no date column exists for the requested
    entity, state that in the fallback message (rule 16).
18. Exclude NULL values from aggregations and counts unless the user
    explicitly asks to include missing/empty values.
19. If a question is ambiguous (e.g., "top" or "best" without a clear
    metric), choose the most obviously relevant numeric column from the
    schema and proceed — do not ask a clarifying question, since only
    one query can be returned.
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
#Lk

# ===========================
# Dashboard Statistics
# =========================== 
# Lk

def get_total_buses():
    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM buses")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def get_total_drivers():
    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM drivers")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def get_total_tickets():
    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tickets")
        return cursor.fetchone()[0]
    finally:
        conn.close()


"""def get_total_companies():
    conn = sqlite3.connect(DB_FILE)

    try:
        cursor = conn.cursor()
<<<<<<< HEAD
        cursor.execute("SELECT COUNT(*) FROM transportation_companies")
=======
        cursor.execute(
            "SELECT COUNT(*) FROM transportation_companies"
        )
>>>>>>> origin/database-backend
        return cursor.fetchone()[0]

    finally:
        conn.close()"""
