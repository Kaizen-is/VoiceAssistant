import re

from jarvis.skills import system


def test_get_time_format():
    out = system.get_time()
    assert re.fullmatch(r"It is \d{2}:\d{2}", out), out


def test_get_date_starts_with_today_is():
    out = system.get_date()
    assert out.startswith("Today is ")
    # Format like "Today is Sunday, August 16, 2026"
    assert "," in out


def test_get_system_stats_has_cpu_and_memory():
    out = system.get_system_stats()
    assert re.fullmatch(
        r"CPU \d+ percent, memory \d+ percent", out
    ), out


def test_get_battery_returns_nonempty_string():
    out = system.get_battery()
    assert isinstance(out, str) and out
    # Either a desktop message or the "Battery at N percent, ..." shape
    assert ("battery" in out.lower()) or ("desktop" in out.lower())
