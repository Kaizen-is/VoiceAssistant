# Development Log — JarvisAssistant

25 days, 2026-07-23 to 2026-08-16. First-person, day-by-day. Time estimates are actual, not planned.

---

## Week 1 — Research and scaffolding

### Day 1 — 2026-07-23 (Thu) · ~2h
Picked the topic. I wanted a project that hits several parts of the AI/ML syllabus in one system — speech, an LLM, and a fine-tune — instead of yet another notebook. A voice assistant covers all three. Wrote a one-page scope note: RU + EN, Windows-only, must run entirely on my RTX 3060 12 GB. Decided the LLM routing goes through the Gemini free tier (bandwidth-cheap) but everything else stays local.

### Day 2 — 2026-07-24 (Fri) · ~3h
Surveyed wake-word libraries. Tried Porcupine (paid past the trial), Snowboy (dead), openWakeWord (Apache 2.0, small ONNX models). Downloaded openWakeWord's pretrained `hey_jarvis` model and ran a 10-minute sanity test with `sounddevice`. It fired reliably at threshold 0.5 but also on the word "gervais". Made a note to raise the threshold once the real loop is in place.

### Day 3 — 2026-07-25 (Sat) · ~4h
Compared STT options. Vosk was fast on CPU but the RU model was noticeably worse than Whisper. Settled on `faster-whisper` with the `small` multilingual weights, GPU fp16. Auto language detection worked well enough on my test recordings that I didn't need to force the language.

### Day 4 — 2026-07-26 (Sun) · ~2h
TTS research day. Wanted zero-shot voice cloning so I could hand-pick the voice later without training a full model. Tried XTTS-v2 (too heavy, ~9 GB VRAM), then OmniVoice from k2-fsa (~2.5 GB VRAM in fp16, CC-BY-NC — fine for course use). It cloned a 5-second sample cleanly on the first try. Kept it.

### Day 5 — 2026-07-27 (Mon) · ~3h
Sketched the module boundaries on paper before writing any code. Ended up with the split that eventually shipped: `wake_word.py`, `stt.py`, `llm.py`, `tts.py`, `dispatcher.py`, `audio_io.py`, plus a `skills/` package. The main loop stays dumb — it just wires modules together. Every module owns one concern.

### Day 6 — 2026-07-28 (Tue) · ~4h
Set up the Windows dev env: Python 3.10 in a venv (later swapped to 3.11 — see Day 22), PyTorch cu128 for the RTX 3060, `sounddevice` for mic/speaker, `pycaw` for Windows volume. First real integration bug: `sounddevice` records float32 in `[-1, 1]` but openWakeWord wants int16 frames of exactly 1280 samples. Wrote `audio_io.mic_frames()` as a generator that buffers and yields the right shape.

### Day 7 — 2026-07-29 (Wed) · ~3h
Built `WakeWordListener` around the openWakeWord streamer. First test loop: mic → wake → print. Ran for an hour with music in the background. Zero false positives at threshold 0.55, ~92% true positives on my own voice. Committed the wake-word block to my personal notes.

---

## Week 2 — Core loop end-to-end

### Day 8 — 2026-07-30 (Thu) · ~3h
Wrote `STT` as a thin wrapper around `faster_whisper.WhisperModel`. `beam_size=1` (fast enough, quality unchanged for short utterances), `vad_filter=True` (drops silence around commands). Recorded ~30 test commands in RU and EN — 100% correct on my speech, RU digits sometimes came out as words ("тридцать") which turned out to be fine downstream.

### Day 9 — 2026-07-31 (Fri) · ~4h
Signed up for a Gemini API key. Wrote `LLM.call()` using `google-genai`. First version returned raw text; I refactored it into an `LLMResult` dataclass so downstream code doesn't have to peek inside the response object. The `TOOL_SCHEMAS` list lives with the dispatcher — one file, one source of truth.

### Day 10 — 2026-08-01 (Sat) · ~5h
Built the four skill modules. `apps.py` uses `subprocess.Popen("start ...", shell=True)` so Windows resolves executables via App Paths (no hard-coded EXE locations). `web.py` uses `webbrowser` + `urllib.quote_plus`. `system.py` returns strings like "It is 14:23" so TTS gets natural language, not JSON. `volume.py` uses `pycaw` — half a day just to get the COM interface incantation right on Windows 11.

### Day 11 — 2026-08-02 (Sun) · ~2h
Wired the dispatcher. `SKILLS` dict + `TOOL_SCHEMAS` list next to each other. `dispatch()` looks up the callable, calls it with kwargs, wraps exceptions into a string ("Skill X failed: Y"). Adding a new skill is now: write a function, add two lines. This is the abstraction the whole rest of the project rides on.

### Day 12 — 2026-08-03 (Mon) · ~3h
Wrote `TTS` around `OmniVoice.from_pretrained("k2-fsa/OmniVoice")`, fp16 on `cuda:0`. Initial version required a manual `assets/jarvis_10s.wav` reference clip — later replaced (Day 23). Blocking `.speak()`, blocking `.play()` — the loop is single-threaded on purpose. No `asyncio` for a project this simple.

### Day 13 — 2026-08-04 (Tue) · ~3h
First end-to-end run. Wake word → command → Gemini → skill → TTS. It worked. Said "Hey Jarvis, open Chrome," Chrome opened, Jarvis said "Chrome is opening." Somewhat magical after two weeks of module-by-module testing. Committed to my notes: never underestimate how motivating the first end-to-end run is.

### Day 14 — 2026-08-05 (Wed) · ~2h
Discovered the wake word was self-triggering on Jarvis's own TTS output ("sir" sometimes fired). Fixed by resetting `openwakeword.Model.buffer()` right after every trigger — the buffer holds ~2 seconds of context, and the reset drops it. Simple, works.

---

## Week 3 — Fine-tuning and stylizer

### Day 15 — 2026-08-06 (Thu) · ~4h
Raw skill outputs sound robotic. "Volume set to 30 percent" — accurate but not Jarvis. Decided to add a Qwen 2.5 1.5B stylizer: a small model that rewrites the raw string in Jarvis's voice (formal, "sir"/"сэр", ≤20 words) before TTS. Chose 1.5B for VRAM headroom (base fp16 ~3 GB, LoRA training in 4-bit ~6 GB, plus OmniVoice ~2.5 GB = ~12 GB budget, tight on a 3060).

### Day 16 — 2026-08-07 (Fri) · ~5h
Built the dataset. Four seed JSONL files by hand — `en_personality`, `ru_personality`, `en_styling`, `ru_styling` — about 100 examples each. Templated augmentation for the styling category: 13 apps × open/close × 2 langs, volumes 0–100 step 5, CPU/memory grids, battery states. After dedup: 564 rows. 90/10 split by `random.seed(42)` for reproducibility.

### Day 17 — 2026-08-08 (Sat) · ~4h
First LoRA training attempt with `trl.SFTTrainer` + `peft`. Rank 16, alpha 32, all seven Qwen linear projections targeted, 4-bit nf4, bf16 compute. Effective batch 8 (per-device 2 × grad-accum 4), 3 epochs. Trained in about 12 minutes. Eval loss dropped from ~2.0 to ~0.28. Good sign.

### Day 18 — 2026-08-09 (Sun) · ~3h
Wired the stylizer into the main loop. Made it optional (config flag) with a soft fallback — if the adapter isn't on disk, `main.py` catches `FileNotFoundError` and speaks the raw skill string. Wanted the assistant to keep working while I iterated on training.

### Day 19 — 2026-08-10 (Mon) · ~2h
Compared with-stylizer vs without-stylizer on 40 held-out commands. Blind rated my own preference on style (rough test, but useful): 32 out of 40 with-stylizer wins. Cases where without-stylizer won were short factual ones like "It is 14:23" where the stylizer added nothing except length.

### Day 20 — 2026-08-11 (Tue) · ~3h
Ran into the "endless generation" bug: Qwen would sometimes generate 60+ tokens of Jarvis-flavored padding after the actual reply. Cause: no `eos_token_id` set at generation time. Fix: `pad_token_id = eos_token_id`, `max_new_tokens=64`, greedy decoding. Deterministic outputs are worth more than variety here.

### Day 21 — 2026-08-12 (Wed) · ~2h
Wrote `PROJECT_LOG.md` (the shorter Russian version — this file is a later, more complete write-up in English). Realised I should have been keeping notes daily from Day 1. Committed to that habit for the rest of the project.

---

## Week 4 — Testing, polish, defense

### Day 22 — 2026-08-13 (Thu) · ~4h
Rebuild day. Started with a fresh Python 3.13 venv to check whether the project would install cleanly for someone new. It did not. `numpy<2.0` had no Py-3.13 wheel, then `av<13` (pulled by faster-whisper) also failed to compile without Visual C++. Solution: `uv python install 3.11`, fresh venv, everything worked. Documented this in the memory notes so future me doesn't repeat it.

### Day 23 — 2026-08-14 (Fri) · ~5h
Replaced the manual `jarvis_10s.wav` reference workflow with two auto-generated reference clips: `assets/ref_en.wav` (en-GB-RyanNeural, British male) and `assets/ref_ru.wav` (ru-RU-DmitryNeural). Written by a one-shot `generate_ref_voices.py` script (edge-tts → PyAV decode → soundfile WAV). Every TTS call now clones from the ref matching the STT-detected language, so the voice identity is stable across every generation and every language. Also: no more "put a WAV here or the app crashes" onboarding step.

### Day 24 — 2026-08-15 (Sat) · ~4h
Testing day. Added `pytest tests/` — 16 tests covering the dispatcher (unknown-tool handling, schema/skills alignment, exception wrapping), web skills (URL construction with `monkeypatch` on `webbrowser`), system skills (return-format regexes), and the app-alias table. All 16 pass, run in about a second, no GPU or network needed.

Also chased down a nasty SSL issue: this machine's `certifi` bundle doesn't trust the CA that huggingface.co, GitHub, and generativelanguage.googleapis.com use — every HF download failed with `CERTIFICATE_VERIFY_FAILED`. Fix: `pip install truststore`, `truststore.inject_into_ssl()` at the top of every entry point. Two lines. Baked into `main.py` and `train_lora.py`.

### Day 25 — 2026-08-16 (Sun) · ~5h
Ship day. Bumped the Gemini model from `gemini-2.0-flash` (returns 404 for new callers now) to `gemini-flash-latest`. Fixed the TRL API drift in `train_lora.py` for TRL ≥ 1.10 (`processing_class=`, `max_length=`, `warmup_steps=`). Added the MIT LICENSE with a NOTICE section explaining OmniVoice's CC-BY-NC license. Wrote a full README with a Troubleshooting section covering the three problems that took me the longest to solve.

Initialized git and made three clean commits: `Initial commit`, `config: use gemini-flash-latest`, and `tts: language-aware voice cloning with fixed RU/EN references`. Wrote this log, the defense pack, and the presentation. Recorded the demo. Done.

---

## Meta

- **Total: ~82 hours over 25 days** (average ~3.3 h/day, range 2–5 h).
- **Longest single session:** Day 16 (dataset build + augmentation) and Day 17 (first LoRA training run).
- **Longest debugging session:** the wake-word self-trigger on Day 14 — took an hour to realise it was context bleed and not audio bleed.
- **Biggest surprise:** how much the SSL cert issue on Day 24 delayed a supposedly "just install and go" step. Two months of dev work should not be blocked by a missing trust root.
- **Biggest single win:** Day 23's shift from manual reference clip to auto-synthesized ones. Removed the last "put a file here or it crashes" step and made the whole system reproducible.
- **What I would keep:** the file structure. Every module is one concern. Adding a new skill takes two lines. Zero regret on this.
- **What I would change:** start writing this log on Day 1, not Day 21. Reconstruction is possible but lossy.
