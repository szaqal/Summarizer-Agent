import requests
from bs4 import BeautifulSoup


class PermanentFetchError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}")


def get_text(url: str) -> str:
    response = requests.get(url, timeout=30)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        code = response.status_code
        if 400 <= code < 500 and code != 429:
            raise PermanentFetchError(code)
        raise
    soup = BeautifulSoup(response.text, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)
