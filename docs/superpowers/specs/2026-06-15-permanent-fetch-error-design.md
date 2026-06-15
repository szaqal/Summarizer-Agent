# Design: Permanent Fetch Error Handling

**Date:** 2026-06-15

## Problem

When `fetcher.get_text` encounters a 4xx HTTP response (e.g. 401, 403, 404), the article stays `summary IS NULL` in the database. On every subsequent run it is retried, fails again, and is skipped — indefinitely. This wastes time and API calls.

## Goal

Articles that fail with a permanent HTTP error are marked in the database so they are never retried.

## Schema Change

```sql
ALTER TABLE rss_items
  ADD COLUMN IF NOT EXISTS fetch_error TEXT;
```

`fetch_error` stores the HTTP status code as a string (`'403'`, `'404'`, etc.) when a permanent fetch failure occurs. NULL means the article has not yet been attempted or was fetched successfully.

## Definition of "Permanent"

Any 4xx HTTP status code **except 429** (Too Many Requests). 429 is a rate limit signal and should remain retriable. 5xx errors and network-level failures (timeouts, connection errors) are also retriable and are not affected by this change.

## Fetcher (`fetcher.py`)

A new exception class is added:

```python
class PermanentFetchError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}")
```

`get_text` is updated to catch `requests.HTTPError` after `raise_for_status()`. If the response status is 4xx and not 429, it raises `PermanentFetchError(status_code)`. All other errors propagate unchanged.

## Database (`db.py`)

A new function is added:

```python
def store_fetch_error(article_id: int, status_code: int) -> None:
    # UPDATE rss_items SET fetch_error = %s WHERE id = %s
```

`fetch_unsummarized` gains `AND fetch_error IS NULL` in its WHERE clause so permanently-errored articles are excluded from all future runs.

## Orchestration (`main.py`)

The `except Exception` block in the processing loop is split:

- `PermanentFetchError` → calls `store_fetch_error(article_id, exc.status_code)`, logs `SKIP (permanent) {url}: HTTP {code}`
- All other exceptions → existing behaviour, logs `SKIP {url}: {exc}`

## Migration

The `fetch_error` column is added via a new SQL migration file, consistent with the existing `db_migration.sql` pattern.

## Files Changed

| File | Change |
|---|---|
| `db_migration_fetch_error.sql` | Add `fetch_error TEXT` column |
| `summarizer_agent/fetcher.py` | Add `PermanentFetchError`; catch and re-raise from `get_text` |
| `summarizer_agent/db.py` | Add `store_fetch_error`; update `fetch_unsummarized` query |
| `summarizer_agent/main.py` | Split except block to handle `PermanentFetchError` |
