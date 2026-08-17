# Capstone Worksheet — JarvisAssistant

One page. Every section answers the question the examiner will ask.

---

## 1. Problem

Voice assistants (Siri, Alexa, Google Assistant) are cloud-only, English-first, and impossible to extend without vendor SDKs. A bilingual (Russian/English) user on a Windows PC who wants to open apps, control volume, and search the web by voice has no privacy-preserving local option that they can actually modify.

**Concrete gap:** no free, open, locally-hostable voice assistant that (a) handles RU + EN in one binary, (b) lets you add a new command in two lines of Python, and (c) uses a fine-tunable LLM for response style.

## 2. Method

A pipeline of five stages, each an off-the-shelf model wired together by a single Python loop:

1. **Wake word** — `openWakeWord` pretrained `hey_jarvis` (ONNX, 2 MB, always-on, ~1% CPU)
2. **STT** — `faster-whisper small` on GPU (fp16, VAD-filtered, auto RU/EN detection)
3. **Intent routing** — Google Gemini `gemini-flash-latest` with function calling, 13 tool schemas
4. **Skills** — plain Python functions that call Windows APIs (subprocess, pycaw, webbrowser, psutil)
5. **Voice** — Qwen 2.5 1.5B + Jarvis LoRA rewrites raw skill output in a formal voice, then OmniVoice clones to a fixed per-language reference clip

The fine-tune is a rank-16 LoRA over all 7 Qwen linear projections, trained on 508 hand-plus-templated bilingual examples in 4-bit nf4 with `trl.SFTTrainer`.

## 3. Evidence

| Claim | Where to look |
|---|---|
| Full loop actually runs | `python main.py`, then say "Hey Jarvis, open Chrome" |
| Fine-tune converges | `train_lora.py` output: eval loss 0.256, token accuracy 93.5% |
| Adding a skill is 2 lines | `jarvis/dispatcher.py` — one line in `SKILLS`, one in `TOOL_SCHEMAS` |
| Bilingual works | STT auto-detects, LLM system prompt is bilingual, TTS has RU and EN refs |
| Tested | `pytest tests/` — 16 tests, ~1 s runtime, all green |
| Reproducible from clean install | `README.md` Setup section; verified on a fresh Python 3.11 venv |
| Voice is consistent | `assets/ref_en.wav` and `assets/ref_ru.wav` are checked in — same reference on every generation |

## 4. What I did NOT do (gaps)

- **No streaming STT.** Whisper is called on a fixed 5-second clip. A better product would VAD-trigger and record variable length. Deliberately scoped out — adds complexity, no course points for it.
- **No multi-turn conversation.** Every command is stateless. Adding memory would require a session store and prompt-template changes. Out of scope.
- **No hotword personalization.** `hey_jarvis` is speaker-independent, which means false positives on other people saying "Jarvis" nearby. Would need a small speaker-embedding model to filter.
- **Windows-only.** `pycaw` is Windows-specific. Linux/macOS would require different backends for volume and app launching.
- **OmniVoice is CC-BY-NC.** Fine for a course project, blocks commercial use. Swapping the TTS backend is the migration path.

## 5. Next

If I had another two weeks:
1. **Streaming STT with silence-based end-of-utterance** — would kill the fixed-5-second wait.
2. **Per-user wake word fine-tune** — 50 samples of "Hey Jarvis" from me, LoRA-finetune openWakeWord's classifier head, drop the false-positive rate to near zero.
3. **Add skills for calendar, email, and system search** — the dispatcher was designed to make this easy; the ceiling is my API-plumbing time, not the framework.

## 6. Risks and honest caveats

- **API dependency:** Gemini free-tier rate limits (~15 requests/min) will bite in a heavy demo. Fallback plan: swap to a local 7 B model via `llama-cpp-python` — the `LLM` class already abstracts this behind `call()`.
- **OmniVoice on GPU:** ~2.5 GB VRAM. On my 12 GB card, plus Qwen 1.5B in 4-bit (~1 GB) plus Whisper small in fp16 (~1 GB), I sit at ~5 GB during idle and ~7 GB during a full turn. Room to grow to Whisper `medium` or Qwen 3 B before things get tight.
- **Voice cloning ethics:** the reference clips are AI-generated Microsoft voices, not a real person's voice, precisely to sidestep this. If someone drops a real person's clip into `assets/`, they own that decision.

---

**Single-sentence summary:** JarvisAssistant is a bilingual, locally-hosted, Windows-native voice assistant with a fine-tuned Qwen stylizer and language-consistent voice cloning, extensible by writing two lines of Python per new skill.
