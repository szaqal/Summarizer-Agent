# Real Database Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the summarizer agent to the real `rss_items` table on `192.168.18.36`, limit each run to 50 articles, write Polish summaries, and include article titles in the Signal digest.

**Architecture:** Five targeted edits across five files — `.env`, `db_migration.sql`, `db.py`, `summarizer.py`, `notifier.py` — plus a one-line unpack change in `main.py`. No new files, no structural changes.

**Tech Stack:** Python, psycopg2, LangChain, Mistral API, signal-cli

---

### Task 1: Update `.env` and `db_migration.sql`

**Files:**
- Modify: `.env`
- Modify: `db_migration.sql`

- [ ] **Step 1: Update `.env` with real connection string**

Open `/home/malczyk/Devel/repos/Summarizer-Agent/.env` and set:

```
DATABASE_URL=postgresql://super:super123@192.168.18.36/feeds
```

Leave all other vars (`MISTRAL_API_KEY`, `SIGNAL_RECIPIENT`, `SIGNAL_SENDER`) unchanged.

- [ ] **Step 2: Update `db_migration.sql` to target `rss_items`**

Replace the contents of `/home/malczyk/Devel/repos/Summarizer-Agent/db_migration.sql` with:

```sql
ALTER TABLE rss_items
  ADD COLUMN IF NOT EXISTS summary       TEXT,
  ADD COLUMN IF NOT EXISTS summarized_at TIMESTAMPTZ;
```

- [ ] **Step 3: Run the migration**

```bash
cd /home/malczyk/Devel/repos/Summarizer-Agent
PGPASSWORD=super123 psql -h 192.168.18.36 -U super -d feeds -f db_migration.sql
```

Expected output:
```
ALTER TABLE
```

Then verify the columns exist:

```bash
PGPASSWORD=super123 psql -h 192.168.18.36 -U super -d feeds -c "\d rss_items" | grep -E "summary|summarized_at"
```

Expected: two rows showing `summary | text` and `summarized_at | timestamp with time zone`.

- [ ] **Step 4: Commit**

```bash
git add db_migration.sql
git commit -m "feat: update migration to target rss_items table"
```

Note: `.env` is gitignored and must not be committed.

---

### Task 2: Update `db.py`

**Files:**
- Modify: `summarizer_agent/db.py`

Current file queries `articles` and returns `(id, url)`. This task changes it to query `rss_items`, return `(id, title, url)`, and add `LIMIT 50`.

- [ ] **Step 1: Replace `db.py` with the updated version**

```python
import psycopg2

from summarizer_agent.config import DATABASE_URL


def fetch_unsummarized() -> list[tuple[int, str, str]]:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, url FROM rss_items"
                " WHERE summary IS NULL ORDER BY id LIMIT 50"
            )
            return cur.fetchall()


def store_summary(article_id: int, summary: str) -> None:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE rss_items SET summary = %s, summarized_at = NOW() WHERE id = %s",
                (summary, article_id),
            )
        conn.commit()
```

- [ ] **Step 2: Smoke-test the DB connection**

```bash
cd /home/malczyk/Devel/repos/Summarizer-Agent
.venv/bin/python -c "
from summarizer_agent.db import fetch_unsummarized
rows = fetch_unsummarized()
print(f'Fetched {len(rows)} rows')
print('First row:', rows[0] if rows else 'none')
"
```

Expected: `Fetched 50 rows` and a tuple of `(int, str, str)` for the first row (id, title, url).

- [ ] **Step 3: Commit**

```bash
git add summarizer_agent/db.py
git commit -m "feat: query rss_items with title and limit 50"
```

---

### Task 3: Update `summarizer.py` — Polish prompt

**Files:**
- Modify: `summarizer_agent/summarizer.py`

- [ ] **Step 1: Replace the prompt string**

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

from summarizer_agent.config import MISTRAL_API_KEY

_prompt = ChatPromptTemplate.from_template(
    "Streść poniższy artykuł w 3-5 zdaniach po polsku:\n\n{text}"
)
_llm = ChatMistralAI(model="mistral-small-latest", api_key=MISTRAL_API_KEY)
_chain = _prompt | _llm | StrOutputParser()


def summarize(text: str) -> str:
    return _chain.invoke({"text": text})
```

- [ ] **Step 2: Smoke-test the Polish prompt**

```bash
cd /home/malczyk/Devel/repos/Summarizer-Agent
.venv/bin/python -c "
from summarizer_agent.summarizer import summarize
result = summarize('Złoto to metal szlachetny używany jako środek przechowywania wartości.')
print(result)
"
```

Expected: a 3–5 sentence Polish summary string, no exceptions.

- [ ] **Step 3: Commit**

```bash
git add summarizer_agent/summarizer.py
git commit -m "feat: use Polish summarization prompt"
```

---

### Task 4: Update `notifier.py` — include title in digest

**Files:**
- Modify: `summarizer_agent/notifier.py`

Current `send()` takes `list[tuple[str, str]]` (url, summary). This task changes it to `list[tuple[str, str, str]]` (title, url, summary) and updates the digest format.

- [ ] **Step 1: Replace `notifier.py` with the updated version**

```python
import subprocess

from summarizer_agent.config import SIGNAL_RECIPIENT, SIGNAL_SENDER


def send(summaries: list[tuple[str, str, str]]) -> None:
    header = f"Digest — {len(summaries)} artykuł(y)\n"
    parts = [f"{title}\n{url}\n{summary}" for title, url, summary in summaries]
    message = header + "\n\n---\n\n".join(parts)
    subprocess.run(
        ["signal-cli", "-a", SIGNAL_SENDER, "send", "-m", message, SIGNAL_RECIPIENT],
        check=True,
    )
```

- [ ] **Step 2: Commit**

```bash
git add summarizer_agent/notifier.py
git commit -m "feat: include article title in Signal digest"
```

---

### Task 5: Update `main.py` — unpack title

**Files:**
- Modify: `summarizer_agent/main.py`

Current loop unpacks `(article_id, url)`. This task changes it to unpack `(article_id, title, url)` and pass title to `send()`.

- [ ] **Step 1: Replace `main.py` with the updated version**

```python
import sys

from summarizer_agent.db import fetch_unsummarized, store_summary
from summarizer_agent.fetcher import get_text
from summarizer_agent.notifier import send
from summarizer_agent.summarizer import summarize


def main() -> None:
    articles = fetch_unsummarized()
    if not articles:
        print("No unsummarized articles found.", file=sys.stderr)
        return

    collected: list[tuple[str, str, str]] = []

    for article_id, title, url in articles:
        try:
            text = get_text(url)
            summary = summarize(text)
            store_summary(article_id, summary)
            collected.append((title, url, summary))
            print(f"OK  {url}", file=sys.stderr)
        except Exception as exc:
            print(f"SKIP {url}: {exc}", file=sys.stderr)

    if collected:
        send(collected)
        print(f"Digest sent ({len(collected)} articles).", file=sys.stderr)
    else:
        print("No summaries produced; Signal notification skipped.", file=sys.stderr)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: End-to-end smoke test (single article)**

Temporarily limit to 1 article to keep cost and time low. In a Python shell:

```bash
cd /home/malczyk/Devel/repos/Summarizer-Agent
.venv/bin/python -c "
from summarizer_agent.db import fetch_unsummarized, store_summary
from summarizer_agent.fetcher import get_text
from summarizer_agent.summarizer import summarize

rows = fetch_unsummarized()
article_id, title, url = rows[0]
print('Title:', title)
print('URL:', url)
text = get_text(url)
summary = summarize(text)
print('Summary:', summary)
store_summary(article_id, summary)
print('Stored OK')
"
```

Expected: title and URL printed, a Polish 3–5 sentence summary printed, then `Stored OK`. No exceptions.

Verify in the database:

```bash
PGPASSWORD=super123 psql -h 192.168.18.36 -U super -d feeds \
  -c "SELECT id, LEFT(summary,100), summarized_at FROM rss_items WHERE summary IS NOT NULL LIMIT 1"
```

Expected: one row with a non-null summary and timestamp.

- [ ] **Step 3: Commit**

```bash
git add summarizer_agent/main.py
git commit -m "feat: unpack title from fetch_unsummarized and pass to notifier"
```
