import psycopg2

from summarizer_agent.config import DATABASE_URL


def fetch_unsummarized() -> list[tuple[int, str]]:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, url FROM articles WHERE summary IS NULL ORDER BY id")
            return cur.fetchall()


def store_summary(article_id: int, summary: str) -> None:
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE articles SET summary = %s, summarized_at = NOW() WHERE id = %s",
                (summary, article_id),
            )
        conn.commit()
