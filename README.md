# Project A — "Ask your data" chatbot

Ask a question in plain English. The app uses AI to write a database query,
runs it, and shows you the answer along with the query it wrote.

## What's in this folder

- `create_database.py` — makes the sample database (run once).
- `app.py` — the app itself. Your work lives here, marked with `TODO`.
- `requirements.txt` — the list of tools the app needs.

## Setup (do this once)

1. Install the tools:
   ```
   pip install -r requirements.txt
   ```
2. Create the sample database:
   ```
   python create_database.py
   ```
   This makes a file called `transport.db` (a fake online shop). Never use real
   company data here.
3. Add the API key. Create a folder called `.streamlit` and inside it a file
   called `secrets.toml` containing the API key you've been given:
   ```
   ANTHROPIC_API_KEY = "paste-the-key-here"
   ```

## Run it

```
streamlit run app.py
```

A browser tab opens with your app. Every time you save `app.py`, the app
offers to refresh — that's your build-and-see loop.

## Your mission

Get the basic loop working, then improve it. The `TODO`s in `app.py`, in order:

- **TODO 1 — the prompt.** This is the heart of the project. Make the AI write
  better, more reliable SQL by giving it clearer instructions. Watch what it
  gets wrong, then fix it with words.
- **TODO 2 — the safety check.** Only allow harmless read-only queries. Reject
  anything that could change the data before it ever runs.
- **TODO 3 — a chart (Wednesday polish).** When the answer is a category and a
  number, draw a bar chart instead of just a table.

## If you get stuck

Read the red error message out loud — it usually names the exact problem. Most
early errors mean the AI guessed a column that doesn't exist, which you fix by
improving the prompt (TODO 1).
