import psycopg2

from summarizer_agent.config import DATABASE_URL


def fetch_unsummarized() -> list[tuple[int, str, str, object]]:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, url, published_date FROM rss_items"
                " WHERE summary IS NULL AND fetch_error IS NULL ORDER BY id LIMIT 100"
            )
            return cur.fetchall()


def store_fetch_error(article_id: int, status_code: int) -> None:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE rss_items SET fetch_error = %s WHERE id = %s",
                (str(status_code), article_id),
            )
        conn.commit()


def store_summary(article_id: int, summary: str) -> None:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE rss_items SET summary = %s, summarized_at = NOW() WHERE id = %s",
                (summary, article_id),
            )
        conn.commit()
