"""Web actions: search, open URLs. Uses the default browser."""
# Веб-действия: поиск и URL
import webbrowser
from urllib.parse import quote_plus


def youtube_search(query: str) -> str:
    # Собираем URL поиска и открываем в браузере
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    webbrowser.open(url)
    return f"Searching YouTube for {query}"


def google_search(query: str) -> str:
    # Поиск в Google
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    webbrowser.open(url)
    return f"Searching Google for {query}"


def open_url(url: str) -> str:
    # Добавляем протокол если отсутствует
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url}"
