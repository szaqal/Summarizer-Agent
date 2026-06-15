import psycopg2

from summarizer_agent.config import DATABASE_URL


def fetch_unsummarized() -> list[tuple[int, str, str, object]]:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, url, published_date FROM rss_items"
                " WHERE summary IS NULL ORDER BY id LIMIT 100"
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
