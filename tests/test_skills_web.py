from jarvis.skills import web


def test_youtube_search_builds_correct_url(monkeypatch):
    opened = []
    monkeypatch.setattr(web.webbrowser, "open", lambda u: opened.append(u))

    msg = web.youtube_search("python tutorial")

    assert opened == ["https://www.youtube.com/results?search_query=python+tutorial"]
    assert "python tutorial" in msg


def test_google_search_url_encodes_special_chars(monkeypatch):
    opened = []
    monkeypatch.setattr(web.webbrowser, "open", lambda u: opened.append(u))

    web.google_search("hello & world")

    assert opened[0] == "https://www.google.com/search?q=hello+%26+world"


def test_open_url_prepends_https_when_missing(monkeypatch):
    opened = []
    monkeypatch.setattr(web.webbrowser, "open", lambda u: opened.append(u))

    web.open_url("example.com")
    web.open_url("http://example.com")
    web.open_url("https://example.com")

    assert opened == [
        "https://example.com",
        "http://example.com",
        "https://example.com",
    ]
