import sys
import time

from summarizer_agent.db import fetch_unsummarized, store_fetch_error, store_summary
from summarizer_agent.fetcher import PermanentFetchError, get_text
from summarizer_agent.notifier import send
from summarizer_agent.summarizer import summarize


def main() -> None:
    articles = fetch_unsummarized()
    if not articles:
        print("No unsummarized articles found.", file=sys.stderr)
        return

    collected: list[tuple[str, str, str, object]] = []

    for article_id, title, url, published_date in articles:
        try:
            text = get_text(url)
            summary = summarize(text)
            store_summary(article_id, summary)
            collected.append((title, url, summary, published_date))
            print(f"OK  {url}", file=sys.stderr)
        except PermanentFetchError as exc:
            store_fetch_error(article_id, exc.status_code)
            print(f"SKIP (permanent) {url}: {exc}", file=sys.stderr)
        except Exception as exc:
            print(f"SKIP {url}: {exc}", file=sys.stderr)
        time.sleep(8)

    if collected:
        send(collected)
        print(f"Digest sent ({len(collected)} articles).", file=sys.stderr)
    else:
        print("No summaries produced; Signal notification skipped.", file=sys.stderr)


if __name__ == "__main__":
    main()
