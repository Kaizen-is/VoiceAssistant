# Jarvis Voice Assistant

Bilingual (Russian/English) desktop voice assistant for Windows, built as an
AI/ML course project.

**Stack:**
- Wake word: `openWakeWord` (pre-trained `hey_jarvis`, ~2 MB, always-on)
- STT: `faster-whisper` small (multilingual, GPU)
- LLM: Google Gemini API (free tier) with function calling
- TTS: `OmniVoice` 0.6B with zero-shot voice cloning
- Skills: Python functions that call Windows APIs (subprocess, psutil, pycaw, webbrowser)

## Setup (Windows, one time)

Requires **Python 3.10+** and an NVIDIA GPU (RTX 3060 or better recommended).

```powershell
# 1. Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install PyTorch with CUDA first (OmniVoice + Whisper both use it)
pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128

# 3. Install everything else
pip install -r requirements.txt

# 4. Get a free Gemini API key at https://aistudio.google.com/apikey
copy .env.example .env
# Then edit .env and paste your key

# 5. Add a voice reference clip
#    See assets/README.md — drop a 3-10 second WAV named jarvis_10s.wav
#    into the assets/ folder.
```

## Run

```powershell
python main.py
```

First launch downloads model weights (~2 GB total) into your user cache. After
that, startup takes about 10 seconds. Say **"Hey Jarvis"** then your command.

## Fine-tune the response stylizer (optional)

The stylizer rewrites raw skill output in Jarvis's voice ("sir"/"сэр", ≤20 words)
before TTS. Without a trained adapter Jarvis just speaks the raw skill string —
still works, just less flavorful.

```powershell
# 1. Build/refresh the dataset (already checked in, safe to re-run)
python data/build_dataset.py

# 2. Fine-tune Qwen 2.5 1.5B with LoRA (4-bit nf4, ~5-6 GB VRAM, 10-20 min on RTX 3060)
python train_lora.py
```

Output lands at `models/jarvis-lora/` (~30 MB, git-ignored). `main.py` will
pick it up on next run.

## Run tests

```powershell
pip install pytest
pytest tests/
```

Tests cover the dispatcher, the web/system skills, and app aliases. No network,
no GPU, no audio.

## Troubleshooting

- **`FileNotFoundError: assets/jarvis_10s.wav`** — you're missing the voice
  reference clip. Drop a 3-10 s WAV (mono, 16 kHz or higher) into `assets/`.
- **CUDA / GPU not detected** — verify `python -c "import torch; print(torch.cuda.is_available())"`
  returns `True`. If not, reinstall PyTorch with the cu128 wheel per step 2 above.
  As a fallback, set `WHISPER_DEVICE = "cpu"` and `WHISPER_COMPUTE = "int8"` in
  `config.py` (STT works on CPU; the stylizer needs GPU).
- **Wake word triggers on random speech** — raise `WAKE_THRESHOLD` in `config.py`
  (e.g., `0.6` or `0.65`).
- **Wake word never triggers** — lower it slightly, or check your default mic
  in Windows Sound settings.
- **Stylizer disabled: FileNotFoundError** — you haven't trained the adapter
  yet. See "Fine-tune the response stylizer" above. Jarvis still works,
  just speaks raw skill strings.

## Try it

- "Hey Jarvis, open Chrome"
- "Hey Jarvis, find a Python programming video on YouTube"
- "Hey Jarvis, what day is today?"
- "Hey Jarvis, set volume to 30"
- "Джарвис, открой блокнот"
- "Джарвис, какая сейчас загрузка процессора?"

## Adding a new command

1. Write a Python function in the appropriate file under `jarvis/skills/`
   (return a short string — that's what Jarvis will say back).
2. Register it in two places inside `jarvis/dispatcher.py`:
   - Add to the `SKILLS` dict: `"my_skill": my_module.my_skill,`
   - Add its JSON schema to `TOOL_SCHEMAS`.

That's it. The LLM will pick it up automatically on the next call.

## Project layout

```
JarvisAssistant/
├── main.py                # entry loop
├── config.py              # tune model sizes, thresholds, paths here
├── requirements.txt
├── .env                   # your GEMINI_API_KEY (git-ignored)
├── assets/
│   └── jarvis_10s.wav     # voice clone reference (you provide)
└── jarvis/
    ├── audio_io.py        # mic + speaker
    ├── wake_word.py       # openWakeWord
    ├── stt.py             # faster-whisper
    ├── llm.py             # Gemini tool calling
    ├── tts.py             # OmniVoice
    ├── dispatcher.py      # SKILLS registry + tool schemas
    └── skills/
        ├── apps.py        # open/close applications
        ├── web.py         # YouTube, Google, URLs
        ├── system.py      # time, date, CPU, battery
        └── volume.py      # system volume
```

## Licenses & credits
- OmniVoice: **CC-BY-NC** (non-commercial only) — fine for course use.
- Everything else: permissive open source.
