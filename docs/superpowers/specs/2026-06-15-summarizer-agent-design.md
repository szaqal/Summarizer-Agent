# Summarizer Agent — Design Spec

**Date:** 2026-06-15
**Status:** Approved

## Overview

A manually-triggered Python script that reads article URLs from a PostgreSQL database, fetches and summarizes each article using LangChain + Mistral API, stores summaries back into the database, and delivers a consolidated digest via signal-cli.

## Goals

- Fetch unsummarized article URLs from Postgres
- Retrieve article content via HTTP and extract readable text
- Summarize each article using Mistral (via LangChain)
- Persist summaries to the database
- Send a single digest message over Signal
- Run manually; cron scheduling deferred to a later iteration

## Non-Goals

- Scheduling / daemon mode (future work)
- Web UI or API
- Multi-LLM support
- Article deduplication or crawling

## Project Structure

```
summarizer_agent/
├── main.py          # orchestrates the full run
├── db.py            # postgres: fetch URLs, store summaries
├── fetcher.py       # HTTP fetch + extract plain text from HTML
├── summarizer.py    # LangChain + Mistral summarization chain
├── notifier.py      # subprocess wrapper for signal-cli
├── config.py        # env var loading (DB URL, Mistral key, Signal recipient)
requirements.txt
.env                 # gitignored — contains secrets
```

## Database Schema

Assumes an existing `articles` table extended with:

```sql
ALTER TABLE articles
  ADD COLUMN summary       TEXT,
  ADD COLUMN summarized_at TIMESTAMPTZ;
```

`summary IS NULL` is the marker for unprocessed rows. Both columns are written atomically on success.

## Data Flow

```
main.py
  └─ db.fetch_unsummarized()         → [(id, url), ...]
       └─ for each (id, url):
            fetcher.get_text(url)    → plain text string
            summarizer.summarize()   → summary string
            db.store_summary()       → writes summary + summarized_at
  └─ notifier.send(digest)           → signal-cli subprocess call
```

Failed articles (HTTP error, parse failure, LLM error) are logged and skipped — they remain with `summary IS NULL` for the next run.

## Components

### `config.py`
Loads from environment via `python-dotenv`:
- `DATABASE_URL` — Postgres connection string
- `MISTRAL_API_KEY` — Mistral API key
- `SIGNAL_RECIPIENT` — phone number or group ID for Signal delivery
- `SIGNAL_SENDER` — registered Signal account number

### `db.py`
- `fetch_unsummarized() -> list[tuple[int, str]]` — `SELECT id, url FROM articles WHERE summary IS NULL`
- `store_summary(id: int, summary: str) -> None` — updates `summary` and `summarized_at = NOW()`

Uses `psycopg2`. Connection managed with a context manager; no connection pool needed for a single-run script.

### `fetcher.py`
- `get_text(url: str) -> str` — HTTP GET with `requests`, parse with `BeautifulSoup`, return visible text stripped of scripts and styles.
- Raises on non-200 or network error; caller handles by logging and skipping.

### `summarizer.py`
LangChain LCEL chain:
```python
prompt = ChatPromptTemplate.from_template(
    "Summarize the following article in 3-5 sentences:\n\n{text}"
)
llm = ChatMistralAI(model="mistral-small-latest", api_key=MISTRAL_API_KEY)
chain = prompt | llm | StrOutputParser()
```
- `summarize(text: str) -> str` — calls `chain.invoke({"text": text})`

### `notifier.py`
- `send(message: str) -> None` — calls `signal-cli -a <SIGNAL_SENDER> send -m <message> <SIGNAL_RECIPIENT>` via `subprocess.run(..., check=True)`.
- Digest format: summaries joined by `\n\n---\n\n`, prefixed with a header line.

### `main.py`
```
1. fetch_unsummarized()
2. for each article:
     a. get_text(url)        [skip on error]
     b. summarize(text)      [skip on error]
     c. store_summary(id, s)
3. build digest from collected summaries
4. send(digest) if any summaries collected
```

## Dependencies

```
langchain
langchain-mistralai
psycopg2-binary
requests
beautifulsoup4
lxml
python-dotenv
```

## Error Handling

- Per-article errors are caught, logged to stderr, and skipped. The article stays unprocessed for the next run.
- If zero articles are summarized, Signal is not called.
- Fatal errors (DB connection failure, missing config) propagate and exit with a non-zero code.

## Configuration

All secrets and environment-specific values in `.env` (gitignored). A `.env.example` is committed as a reference.
