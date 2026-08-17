"""Central configuration. Edit values here to tune behavior."""
# Все настройки проекта в одном месте
from pathlib import Path

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"

# --- Wake word / Слово пробуждения ---
WAKE_WORD_MODEL = "hey_jarvis"      # предобученная модель openWakeWord
WAKE_THRESHOLD = 0.55               # выше = меньше ложных срабатываний

# --- Audio / Параметры звука ---
SAMPLE_RATE = 16_000                # 16 кГц — стандарт для Whisper
FRAME_MS = 80                       # длина кадра для детектора
COMMAND_RECORD_SECONDS = 5          # длительность записи команды
SILENCE_THRESHOLD = 0.01            # порог тишины (не используется)

# --- STT / Распознавание речи ---
WHISPER_MODEL_SIZE = "small"        # tiny | base | small | medium | large-v3
WHISPER_DEVICE = "cuda"             # запуск на GPU; "cpu" — запасной
WHISPER_COMPUTE = "float16"         # float16 на GPU, int8 на CPU

# --- LLM / Роутинг команд через Gemini ---
GEMINI_MODEL = "gemini-flash-latest"   # always the current stable Flash model
LLM_SYSTEM_PROMPT = (
    "You are Jarvis, a bilingual (Russian/English) voice assistant "
    "running on the user's Windows PC. When the user gives a command, "
    "call exactly one tool that fulfills it. If no tool fits, respond "
    "briefly in the same language the user spoke. Keep spoken responses "
    "under 20 words — they will be read aloud."
)

# --- TTS / Синтез речи с клоном голоса ---
# Two FIXED reference clips (generated once by generate_ref_voices.py).
# Every response clones from ref_en for English, ref_ru for Russian —
# this keeps the voice identity stable across every generation.
TTS_REF_EN = ASSETS / "ref_en.wav"
TTS_REF_RU = ASSETS / "ref_ru.wav"
# Точный текст эталонов — передаём OmniVoice, чтобы не тратить время на транскрипцию
TTS_REF_TEXT_EN = "Hello sir. All systems are online. I am at your service."
TTS_REF_TEXT_RU = "Здравствуйте, сэр. Все системы работают исправно. Я к вашим услугам."
TTS_DEVICE = "cuda:0"
TTS_OUTPUT_SR = 24_000                       # OmniVoice выдаёт 24 кГц

# --- Response Stylizer / Стилизация ответов (Qwen + LoRA) ---
# Переписывает вывод скиллов в голосе Джарвиса перед TTS.
STYLIZER_ENABLED = True
STYLIZER_BASE = "Qwen/Qwen2.5-1.5B-Instruct"
STYLIZER_ADAPTER = ROOT / "models" / "jarvis-lora"
