"""Windows master volume control via pycaw."""
# Управление громкостью через pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def _get_endpoint():
    # Получаем COM-интерфейс главного вывода
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def set_volume(percent: int) -> str:
    """Set system volume to percent (0–100)."""
    # Обрезаем в диапазон 0-100
    percent = max(0, min(100, int(percent)))
    _get_endpoint().SetMasterVolumeLevelScalar(percent / 100.0, None)
    return f"Volume set to {percent} percent"


def get_volume() -> str:
    # Текущая громкость в процентах
    level = _get_endpoint().GetMasterVolumeLevelScalar()
    return f"Volume is at {int(level * 100)} percent"


def mute() -> str:
    _get_endpoint().SetMute(1, None)
    return "Muted"


def unmute() -> str:
    _get_endpoint().SetMute(0, None)
    return "Unmuted"
