# Evidence Paths — where every artifact lives

The examiner will ask *"can you show me the X?"* This file is the answer: one row per artifact, one path per row, no digging.

---

## 1. Data

| Artifact | Path | Size | What it proves |
|---|---|---|---|
| EN personality seed | `data/en_personality.jsonl` | 115 rows | Hand-written EN examples of the assistant's tone |
| RU personality seed | `data/ru_personality.jsonl` | 110 rows | Same, in Russian |
| EN styling seed | `data/en_styling.jsonl` | 69 rows | Hand-written EN raw-to-styled pairs |
| RU styling seed | `data/ru_styling.jsonl` | 68 rows | Same, in Russian |
| Dataset builder | `data/build_dataset.py` | ~150 lines | Combines seeds + template augmentation + dedup + 90/10 split |
| Final train split | `data/train.jsonl` | 508 rows | What LoRA actually trained on |
| Final val split | `data/val.jsonl` | 56 rows | What eval loss was measured against |

**Demo command:** `python data/build_dataset.py` — regenerates the two split files from the seeds in about a second.

## 2. Code — the actual product

| Concern | Path | Notes |
|---|---|---|
| Entry point / main loop | `main.py` | 76 lines, one loop, no threads |
| Central config | `config.py` | All tunables in one file |
| Wake word | `jarvis/wake_word.py` | openWakeWord streamer, threshold 0.55 |
| STT | `jarvis/stt.py` | faster-whisper small, GPU fp16 |
| LLM routing | `jarvis/llm.py` | Gemini `gemini-flash-latest` + tool calling |
| TTS | `jarvis/tts.py` | OmniVoice, language-aware ref selection |
| Response stylizer | `jarvis/stylize.py` | Qwen 2.5 1.5B + LoRA, 4-bit nf4 |
| Skill dispatcher | `jarvis/dispatcher.py` | SKILLS dict + TOOL_SCHEMAS, single source of truth |
| App skills | `jarvis/skills/apps.py` | Open/close Windows apps with alias table |
| Web skills | `jarvis/skills/web.py` | YouTube / Google search / open URL |
| System skills | `jarvis/skills/system.py` | Time, date, CPU, memory, battery |
| Volume skills | `jarvis/skills/volume.py` | pycaw master volume + mute |
| Audio I/O | `jarvis/audio_io.py` | mic record, speaker play, streaming frames |

## 3. Training pipeline

| Artifact | Path | Notes |
|---|---|---|
| Training script | `train_lora.py` | ~130 lines, one command to fine-tune |
| Trained adapter | `models/jarvis-lora/adapter_model.safetensors` | 74 MB, git-ignored (regenerable) |
| Adapter config | `models/jarvis-lora/adapter_config.json` | LoRA rank, targets, alpha |
| Best-checkpoint trainer state | `models/jarvis-lora/trainer_state.json` | Loss curve, eval metrics per epoch |

**Demo command:** `python train_lora.py` — 6:24 on RTX 3060. Reproducible with `seed=42`.

## 4. Voice identity

| Artifact | Path | Notes |
|---|---|---|
| EN reference clip | `assets/ref_en.wav` | 6.26 s @ 24 kHz, en-GB-RyanNeural |
| RU reference clip | `assets/ref_ru.wav` | 7.78 s @ 24 kHz, ru-RU-DmitryNeural |
| Reference generator | `generate_ref_voices.py` | edge-tts → PyAV → WAV, one-shot |

The two WAVs are tracked in git — they are the voice identity, not throwaway output. If they change, the assistant's voice changes.

## 5. Tests

| Artifact | Path | Runtime |
|---|---|---|
| Dispatcher tests | `tests/test_dispatcher.py` | 6 tests |
| Web skills | `tests/test_skills_web.py` | 3 tests, mocks `webbrowser` |
| System skills | `tests/test_skills_system.py` | 4 tests, format regexes |
| App skills | `tests/test_skills_apps.py` | 3 tests, mocks subprocess |
| **Total** | | **16 tests, ~1 s** |

**Demo command:** `pytest tests/`

## 6. Live demo

The only demo path is:

```powershell
.\.venv\Scripts\python.exe main.py
```

Then, one of:
- "Hey Jarvis, open Chrome"
- "Hey Jarvis, what day is today?"
- "Hey Jarvis, set volume to 30"
- "Джарвис, открой блокнот"
- "Джарвис, какая сейчас загрузка процессора?"

Startup ~10 s (first launch downloads Whisper + Qwen + OmniVoice weights, ~2 GB one-time). Steady-state startup ~3 s.

## 7. Documentation

| Doc | Path |
|---|---|
| User-facing README | `README.md` |
| Original narrative log (Russian, first 15 days) | `PROJECT_LOG.md` |
| Full 25-day dev log (English) | `docs/DEV_LOG_25_DAYS.md` |
| License | `LICENSE` (MIT + NOTICE for OmniVoice CC-BY-NC) |
| Env template | `.env.example` |
| This defense pack | `docs/` |

## 8. Repository

- URL: <https://github.com/Kaizen-is/VoiceAssistant>
- Branch: `main`
- Commits: 3 (initial, Gemini bump, TTS refactor) + this docs commit
- License: MIT with third-party NOTICE
- CI: none (would be a nice next step, but tests run locally in a second)

---

## Analog to standard capstone artifact types

Some rubrics expect specific artifact categories. Here's the mapping:

| Rubric-standard artifact | This project's equivalent |
|---|---|
| Colab notebook | `train_lora.py` (runs standalone, no notebook overhead) |
| Tabular pipeline | N/A — this is a speech project |
| NLP model | Qwen 2.5 1.5B + Jarvis LoRA adapter |
| CV model | N/A |
| Streamlit / web demo | `main.py` — CLI demo, not web-based, but live and observable |
| Dataset | `data/train.jsonl` + `val.jsonl` |
| Test suite | `tests/` |
| Deployment target | Windows PC with Python 3.11 + CUDA 12.8 |
