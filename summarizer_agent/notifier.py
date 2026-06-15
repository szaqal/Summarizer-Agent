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
