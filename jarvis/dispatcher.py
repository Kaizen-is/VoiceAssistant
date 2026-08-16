"""Skill registry + JSON schemas the LLM sees + dispatch helper.

Adding a new skill = write a Python function in jarvis/skills/,
then add one entry to SKILLS and one to TOOL_SCHEMAS below. That's it.
"""
# Реестр скиллов и их схемы для LLM
from jarvis.skills import apps, web, system, volume

# --- Таблица диспетчера: имя → функция ---
SKILLS = {
    "open_application":   apps.open_application,
    "close_application":  apps.close_application,
    "youtube_search":     web.youtube_search,
    "google_search":      web.google_search,
    "open_url":           web.open_url,
    "get_time":           system.get_time,
    "get_date":           system.get_date,
    "get_system_stats":   system.get_system_stats,
    "get_battery":        system.get_battery,
    "set_volume":         volume.set_volume,
    "get_volume":         volume.get_volume,
    "mute":               volume.mute,
    "unmute":             volume.unmute,
}

# --- Схемы для LLM (JSON-schema стиль) ---
TOOL_SCHEMAS = [
    {
        "name": "open_application",
        "description": "Launch a desktop application by common name (Chrome, Notepad, Spotify, Word, VS Code, etc.).",
        "parameters": {
            "type": "object",
            "properties": {"app_name": {"type": "string", "description": "Common name of the app to open."}},
            "required": ["app_name"],
        },
    },
    {
        "name": "close_application",
        "description": "Force-close a running desktop application by name.",
        "parameters": {
            "type": "object",
            "properties": {"app_name": {"type": "string"}},
            "required": ["app_name"],
        },
    },
    {
        "name": "youtube_search",
        "description": "Open YouTube in the browser and search for a query. Use for any request to find, watch, or play videos.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search terms in English."}},
            "required": ["query"],
        },
    },
    {
        "name": "google_search",
        "description": "Open Google search results for a query in the default browser.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "open_url",
        "description": "Open a specific URL in the default browser.",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "Full URL, with or without protocol."}},
            "required": ["url"],
        },
    },
    {
        "name": "get_time",
        "description": "Tell the user the current time.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_date",
        "description": "Tell the user today's date and day of the week.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_system_stats",
        "description": "Report current CPU and memory usage.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_battery",
        "description": "Report battery level and charging state.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "set_volume",
        "description": "Set system master volume to a percentage between 0 and 100.",
        "parameters": {
            "type": "object",
            "properties": {"percent": {"type": "integer", "description": "0 to 100"}},
            "required": ["percent"],
        },
    },
    {
        "name": "get_volume",
        "description": "Report the current system volume level.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "mute",
        "description": "Mute the system master volume.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "unmute",
        "description": "Unmute the system master volume.",
        "parameters": {"type": "object", "properties": {}},
    },
]


def dispatch(tool_name: str, tool_args: dict) -> str:
    """Look up the skill, call it, return the string response for TTS."""
    # Ищем функцию и вызываем с аргументами
    func = SKILLS.get(tool_name)
    if func is None:
        return f"Unknown skill: {tool_name}"
    try:
        return func(**(tool_args or {}))
    except Exception as e:
        # Ошибку возвращаем как строку — озвучится
        return f"Skill {tool_name} failed: {e}"
