"""Launch desktop applications on Windows."""
# Запуск и закрытие приложений
import subprocess

# Псевдонимы для удобных команд голосом
ALIASES = {
    "chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "explorer": "explorer",
    "spotify": "spotify",
    "vscode": "code",
    "vs code": "code",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "telegram": "telegram",
    "discord": "discord",
}


def open_application(app_name: str) -> str:
    """Open a desktop app by common name. Uses Windows `start` so registered
    apps (Chrome, Spotify, ...) resolve via App Paths without hardcoded exes."""
    # Windows сам находит приложение по имени
    target = ALIASES.get(app_name.lower().strip(), app_name)
    subprocess.Popen(f'start "" {target}', shell=True)
    return f"Opening {app_name}"


def close_application(app_name: str) -> str:
    """Force-close all processes matching a given executable name."""
    # Убиваем процесс через taskkill
    exe = ALIASES.get(app_name.lower().strip(), app_name)
    if not exe.endswith(".exe"):
        exe += ".exe"
    subprocess.run(["taskkill", "/F", "/IM", exe],
                   capture_output=True, text=True)
    return f"Closed {app_name}"
