import subprocess

from summarizer_agent.config import SIGNAL_RECIPIENT, SIGNAL_SENDER


def send(summaries: list[tuple[str, str, str, object]]) -> None:
    n = len(summaries)
    header = f"Digest — {n} article(s)\n"
    parts = []
    for title, url, summary, published_date in summaries:
        date_str = str(published_date.date()) if hasattr(published_date, "date") else (str(published_date) if published_date else "")
        date_line = f"{date_str}\n" if date_str else ""
        parts.append(f"{title}\n{date_line}{url}\n{summary}")
    message = header + "\n\n---\n\n".join(parts)
    subprocess.run(
        ["signal-cli", "-a", SIGNAL_SENDER, "send", "-m", message, SIGNAL_RECIPIENT],
        check=True,
    )
