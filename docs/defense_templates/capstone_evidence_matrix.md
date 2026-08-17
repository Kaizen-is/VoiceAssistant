# Capstone Evidence Matrix

Every claim in the pitch, mapped to a file, a line, and a command the examiner can run.

---

## Claim table

| # | Claim (from the pitch) | Evidence artifact | Verification command / file path |
|---|---|---|---|
| 1 | Bilingual — RU and EN in one system | STT auto-language; bilingual system prompt; bilingual dataset; RU+EN reference clips | `config.py:25-31`; `data/*_personality.jsonl`; `assets/ref_*.wav` |
| 2 | Runs locally on RTX 3060 | Model sizes: Whisper small (~1 GB), Qwen 1.5B in 4-bit (~1 GB), OmniVoice (~2.5 GB) | `python -c "import torch; print(torch.cuda.get_device_name(0))"` |
| 3 | Wake-to-speaker ~1.6 s | Measured on Day 24 with 20 samples, median 1.62 s | `DEV_LOG_25_DAYS.md` Day 24; live demo |
| 4 | Two lines to add a skill | `SKILLS` dict + `TOOL_SCHEMAS` list | `jarvis/dispatcher.py:10-24` and `27-117` |
| 5 | Fine-tune converges | Eval loss 0.256, token accuracy 93.5% | `models/jarvis-lora/trainer_state.json` |
| 6 | Trained in 6:24 on 3060 | Trainer log final line: `train_runtime: 384.5` | `models/jarvis-lora/trainer_state.json`; live re-run |
| 7 | LoRA is rank 16, targets all 7 Qwen projections | `LoraConfig(r=16, target_modules=[q,k,v,o,gate,up,down]_proj)` | `train_lora.py:54-62` |
| 8 | 4-bit nf4 quantization | `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', ...)` | `train_lora.py:35-40` and `jarvis/stylize.py:36-40` |
| 9 | Consistent voice per language | Two fixed reference WAVs in `assets/`, `TTS.speak(text, lang)` picks by lang | `jarvis/tts.py:29-40`; play `assets/ref_en.wav` and `assets/ref_ru.wav` |
| 10 | Voice references auto-generated | One-shot edge-tts synthesis | `generate_ref_voices.py`; `python generate_ref_voices.py` |
| 11 | 16 tests, all green | `tests/test_*.py` | `pytest tests/` |
| 12 | Wake-word threshold 0.55 raised from 0.5 | Threshold config; noted false positives at 0.5 on Day 2 | `config.py:10`; `PROJECT_LOG.md` Day 2 |
| 13 | 508 train / 56 val rows, 90/10 split | Dataset stats printed by `build_dataset.py` | `data/train.jsonl` (508 lines); `data/val.jsonl` (56 lines) |
| 14 | Templated augmentation adds ~200 rows | 13 apps × 2 verbs × 2 langs + volumes + CPU/mem + battery | `data/build_dataset.py:53-105` |
| 15 | Dispatcher wraps exceptions cleanly | `try / except / return f"Skill {name} failed: {e}"` | `jarvis/dispatcher.py:126-130` |
| 16 | Windows volume via pycaw COM | `AudioUtilities.GetSpeakers().Activate(...)` | `jarvis/skills/volume.py:8-12` |
| 17 | Gemini uses function calling, not JSON parsing | `types.Tool(function_declarations=TOOL_SCHEMAS)` | `jarvis/llm.py:33` |
| 18 | Wake-word self-trigger fix | `model.reset()` on every trigger | `jarvis/wake_word.py:33` |
| 19 | Reproducible dataset | `random.seed(42)` before shuffle | `data/build_dataset.py:135` |
| 20 | SSL cert workaround for HF/Gemini | `truststore.inject_into_ssl()` at entry-point top | `main.py:5-9` and `train_lora.py:6-11` |
| 21 | Gemini model kept current | Uses `gemini-flash-latest` (2.0-flash was 404'd for new callers on Aug 16) | `config.py:24`; commit `00766dc` |
| 22 | TRL 1.x API compat | `processing_class=`, `max_length=`, `warmup_steps=` — updated from deprecated names | `train_lora.py:81-113`; commit `1ef2b47` |
| 23 | MIT + third-party NOTICE | OmniVoice CC-BY-NC called out in LICENSE | `LICENSE` |
| 24 | Stylizer optional at runtime | `main.py` catches `FileNotFoundError` when adapter is missing | `main.py:26-32` |

## How to read this matrix

1. **Examiner asks a question** — find the claim in column 2.
2. **Read column 4 out loud** as you open the file or type the command.
3. **Show, then explain** — never explain-then-show.

## Anti-pattern

A row that says `Evidence: "in the code"` or `Verification: "trust me"` is not evidence. Every row above names a specific file or a runnable command.
