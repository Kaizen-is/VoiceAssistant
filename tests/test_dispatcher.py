from jarvis.dispatcher import SKILLS, TOOL_SCHEMAS, dispatch


def test_unknown_tool_returns_error_string():
    result = dispatch("no_such_tool", {})
    assert "Unknown skill" in result and "no_such_tool" in result


def test_every_tool_schema_has_a_registered_skill():
    schema_names = {t["name"] for t in TOOL_SCHEMAS}
    assert schema_names == set(SKILLS.keys()), (
        f"Schema/skill mismatch: only in schemas={schema_names - set(SKILLS)}, "
        f"only in SKILLS={set(SKILLS) - schema_names}"
    )


def test_all_skills_are_callable():
    for name, fn in SKILLS.items():
        assert callable(fn), f"{name} is not callable"


def test_dispatch_passes_kwargs(monkeypatch):
    captured = {}

    def fake(**kwargs):
        captured.update(kwargs)
        return "ok"

    monkeypatch.setitem(SKILLS, "open_application", fake)
    out = dispatch("open_application", {"app_name": "Chrome"})
    assert out == "ok"
    assert captured == {"app_name": "Chrome"}


def test_dispatch_wraps_skill_exceptions(monkeypatch):
    def boom(**_):
        raise RuntimeError("kaboom")

    monkeypatch.setitem(SKILLS, "get_time", boom)
    out = dispatch("get_time", {})
    assert "failed" in out and "kaboom" in out


def test_dispatch_handles_missing_args_dict():
    # LLM may return None for tool_args when the tool takes no params
    out = dispatch("get_time", None)
    assert isinstance(out, str) and out
