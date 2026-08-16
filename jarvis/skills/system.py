"""System info skills — time, date, hardware stats."""
# Системная информация: время, дата, железо
from datetime import datetime
import psutil


def get_time() -> str:
    # Текущее время в формате ЧЧ:ММ
    return f"It is {datetime.now().strftime('%H:%M')}"


def get_date() -> str:
    # Дата и день недели
    return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}"


def get_system_stats() -> str:
    # Загрузка процессора и памяти
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    return f"CPU {cpu:.0f} percent, memory {mem:.0f} percent"


def get_battery() -> str:
    # Уровень заряда батареи
    battery = psutil.sensors_battery()
    if battery is None:
        return "No battery detected — this is likely a desktop."
    plugged = "charging" if battery.power_plugged else "on battery"
    return f"Battery at {int(battery.percent)} percent, {plugged}"
