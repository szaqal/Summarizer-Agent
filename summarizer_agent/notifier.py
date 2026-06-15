import subprocess

from summarizer_agent.config import SIGNAL_RECIPIENT, SIGNAL_SENDER


def send(summaries: list[tuple[str, str]]) -> None:
    header = f"Summarizer Agent digest — {len(summaries)} article(s)\n"
    parts = [f"{url}\n{summary}" for url, summary in summaries]
    message = header + "\n\n---\n\n".join(parts)
    subprocess.run(
        ["signal-cli", "-a", SIGNAL_SENDER, "send", "-m", message, SIGNAL_RECIPIENT],
        check=True,
    )
