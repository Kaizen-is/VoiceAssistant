"""Combine the 4 category files, augment templated styling rows, shuffle, split.

Run:
    python data/build_dataset.py

Produces:
    data/train.jsonl   ~90% for LoRA fine-tuning
    data/val.jsonl     ~10% for evaluation
"""
# Сборка финального датасета для обучения
import json
import random
from pathlib import Path

DATA = Path(__file__).parent
FILES = [
    "en_personality.jsonl",
    "ru_personality.jsonl",
    "en_styling.jsonl",
    "ru_styling.jsonl",
]
SEED = 42
VAL_FRACTION = 0.10

# Системный промпт для примеров стилизации
SYS_STYLE = (
    "You are Jarvis. Rephrase the given system output in your characteristic voice "
    "— formal, concise, address the user as 'sir' (English) or 'сэр' (Russian). "
    "Match the language of the input. Keep it under 20 words."
)


def load_jsonl(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def styling_row(user_text: str, assistant_text: str) -> dict:
    # Одна строка датасета в формате messages
    return {"messages": [
        {"role": "system", "content": SYS_STYLE},
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": assistant_text},
    ]}


# --- Аугментация по шаблонам — расширение покрытия --- #

APPS_EN = ["Chrome", "Firefox", "Edge", "Spotify", "Notepad", "Calculator",
           "Explorer", "VS Code", "Word", "Excel", "PowerPoint",
           "Telegram", "Discord"]
APPS_RU = ["Chrome", "Firefox", "Edge", "Spotify", "блокнот", "калькулятор",
           "проводник", "VS Code", "Word", "Excel", "PowerPoint",
           "Telegram", "Discord"]

VOLUMES = list(range(0, 101, 5))          # 0, 5, 10, ..., 100
CPU_MEM_PAIRS = [(c, m) for c in range(0, 101, 15) for m in range(0, 101, 15)][:25]


def augment() -> list[dict]:
    # Генерируем шаблонные примеры для скиллов
    rows: list[dict] = []
    # Приложения — открытие и закрытие
    for app in APPS_EN:
        rows.append(styling_row(f"Opening {app}", f"{app} is opening, sir."))
        rows.append(styling_row(f"Closed {app}", f"{app} has been closed, sir."))
    for app in APPS_RU:
        rows.append(styling_row(f"Открываю {app}", f"{app} открывается, сэр."))
        rows.append(styling_row(f"{app} закрыт", f"{app} закрыт, сэр."))
    # Громкость на разных уровнях
    for v in VOLUMES:
        rows.append(styling_row(f"Volume set to {v} percent",
                                f"Volume adjusted to {v} percent, sir."))
        rows.append(styling_row(f"Volume is at {v} percent",
                                f"Current volume: {v} percent, sir."))
    for v in VOLUMES:
        rows.append(styling_row(f"Громкость установлена на {v} процентов",
                                f"Громкость — {v} процентов, сэр."))
        rows.append(styling_row(f"Громкость на уровне {v} процентов",
                                f"Сейчас {v} процентов, сэр."))
    # CPU/память
    for cpu, mem in CPU_MEM_PAIRS:
        rows.append(styling_row(
            f"CPU {cpu} percent, memory {mem} percent",
            f"CPU at {cpu} percent, memory at {mem}, sir."))
        rows.append(styling_row(
            f"Процессор {cpu} процентов, память {mem} процентов",
            f"Процессор — {cpu}, память — {mem} процентов, сэр."))
    # Батарея
    for pct in range(5, 101, 10):
        state_en = "charging" if pct > 50 else "on battery"
        state_ru = "заряжается" if pct > 50 else "от аккумулятора"
        rows.append(styling_row(
            f"Battery at {pct} percent, {state_en}",
            f"Battery at {pct} percent, {state_en}, sir."))
        rows.append(styling_row(
            f"Батарея {pct} процентов, {state_ru}",
            f"Батарея {pct} процентов, {state_ru}, сэр."))
    return rows


def main() -> None:
    # Загружаем все категории
    rows: list[dict] = []
    for name in FILES:
        loaded = load_jsonl(DATA / name)
        print(f"  {name:<25} {len(loaded):>4} rows")
        rows.extend(loaded)
    seed_count = len(rows)
    print(f"  {'seed total':<25} {seed_count:>4} rows")

    # Добавляем шаблонную аугментацию
    aug = augment()
    print(f"  {'template-augmented':<25} {len(aug):>4} rows")
    rows.extend(aug)

    # Дедупликация по паре (user, assistant)
    seen = set()
    unique = []
    for r in rows:
        key = (r["messages"][1]["content"], r["messages"][2]["content"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    print(f"  {'after dedup':<25} {len(unique):>4} rows")

    # Перемешиваем с фиксированным сидом
    random.seed(SEED)
    random.shuffle(unique)

    # Разбиение на train и val (90/10)
    n_val = max(1, int(len(unique) * VAL_FRACTION))
    val, train = unique[:n_val], unique[n_val:]

    write_jsonl(DATA / "train.jsonl", train)
    write_jsonl(DATA / "val.jsonl", val)
    print(f"\nWrote data/train.jsonl ({len(train)} rows)")
    print(f"Wrote data/val.jsonl   ({len(val)} rows)")


if __name__ == "__main__":
    main()
