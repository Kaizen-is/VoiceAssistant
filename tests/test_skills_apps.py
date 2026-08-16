from jarvis.skills import apps


def test_aliases_map_common_names():
    # A few sanity checks — voice-friendly names resolve to the actual exe base
    assert apps.ALIASES["vscode"] == "code"
    assert apps.ALIASES["vs code"] == "code"
    assert apps.ALIASES["word"] == "winword"
    assert apps.ALIASES["calculator"] == "calc"


def test_open_application_uses_start_command(monkeypatch):
    calls = []

    class FakePopen:
        def __init__(self, cmd, shell=False):
            calls.append((cmd, shell))

    monkeypatch.setattr(apps.subprocess, "Popen", FakePopen)

    msg = apps.open_application("Chrome")

    assert calls == [('start "" chrome', True)]
    assert "Chrome" in msg


def test_close_application_calls_taskkill_with_exe(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr(apps.subprocess, "run", fake_run)

    apps.close_application("notepad")

    assert calls == [["taskkill", "/F", "/IM", "notepad.exe"]]
