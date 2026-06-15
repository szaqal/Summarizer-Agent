# Real Database Wiring — Design Spec

**Date:** 2026-06-15
**Status:** Approved

## Overview

Wire the summarizer agent to the real PostgreSQL database at `192.168.18.36`. The existing `rss_items` table (database `feeds`, user `super`) holds Polish-language financial news articles fetched from RSS feeds. Each run processes up to 50 unsummarized articles, writes Polish summaries back to the database, and sends a Signal digest that includes article titles.

## Database

- **Host:** `192.168.18.36`
- **Database:** `feeds`
- **User:** `super`
- **Table:** `rss_items`
- **Relevant columns:** `id`, `title`, `url`, `published_date`
- **New columns (via migration):** `summary TEXT`, `summarized_at TIMESTAMPTZ`

## Changes Required

### `.env`
```
DATABASE_URL=postgresql://super:super123@192.168.18.36/feeds
```

### `db_migration.sql`
Target `rss_items` instead of `articles`:
```sql
ALTER TABLE rss_items
  ADD COLUMN IF NOT EXISTS summary       TEXT,
  ADD COLUMN IF NOT EXISTS summarized_at TIMESTAMPTZ;
```

### `summarizer_agent/db.py`
- `fetch_unsummarized() -> list[tuple[int, str, str]]` — returns `(id, title, url)`:
  ```sql
  SELECT id, title, url FROM rss_items WHERE summary IS NULL ORDER BY id LIMIT 50
  ```
- `store_summary(id: int, summary: str) -> None` — updates `rss_items` (unchanged logic, table name changes).

### `summarizer_agent/summarizer.py`
Polish prompt:
```python
"Streść poniższy artykuł w 3-5 zdaniach po polsku:\n\n{text}"
```

### `summarizer_agent/notifier.py`
Digest format includes title:
```
Digest — N artykuły

[Tytuł artykułu]
[url]
[streszczenie]

---

[Tytuł artykułu]
...
```
`send()` signature changes from `list[tuple[str, str]]` (url, summary) to `list[tuple[str, str, str]]` (title, url, summary).

### `summarizer_agent/main.py`
Unpack `(article_id, title, url)` from `fetch_unsummarized()` and pass title through to `send()`.

## Non-Goals

- Filtering by `published_date`
- Configurable batch size (50 is hardcoded for now)
- Handling articles whose content is behind a paywall
