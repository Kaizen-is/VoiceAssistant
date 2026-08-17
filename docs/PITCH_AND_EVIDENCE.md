# Pitch and Evidence — Strong vs Weak

Side-by-side examples of how to describe this project. Both versions are true; only one lands.

---

## The 30-second pitch

### ❌ Weak version

> I built a voice assistant. It uses AI. You say something, it does something. I trained a model on it. It works on Windows. It supports two languages.

Six sentences, six things any Siri clone could claim. Nothing specific. Nothing testable. Nothing memorable.

### ✅ Strong version

> JarvisAssistant is a bilingual Windows voice assistant that runs entirely on my RTX 3060. Wake word to speaker takes about 1.6 seconds. Adding a new voice command is two lines of Python. I fine-tuned a Qwen 1.5B stylizer on 508 examples so every response comes out in a consistent Jarvis voice — same identity, English or Russian, every generation, because the TTS clones from a fixed reference clip per language. 16 tests, 3 clean commits, deployable in one command.

**Why it works:** every clause is a specific number or a specific verb. "1.6 seconds," "2 lines," "508 examples," "fixed reference clip," "16 tests." Nothing hand-wavy. Examiner can attack any single claim and I can point at code.

---

## The 3-minute pitch

**Structure:** Problem (30 s) → Solution (60 s) → Novelty (30 s) → Evidence (30 s) → Ask (30 s).

### ❌ Weak version

> Voice assistants are everywhere but they're cloud-only. I built one that runs locally. It has wake word detection, speech-to-text, an LLM for understanding, some skills for actions, and text-to-speech. I trained a small model to make responses sound better. It works in Russian and English. Here are some screenshots. Any questions?

### ✅ Strong version

> **[Problem]** Every mainstream voice assistant lives in someone else's cloud, in English only, and closed to modification. A bilingual Windows user who wants to open Chrome by voice AND own the code has zero good options.
>
> **[Solution]** JarvisAssistant is a five-stage local pipeline: openWakeWord for the hotword, faster-whisper for STT, Gemini function calling for intent, plain-Python skills for the actions, and OmniVoice zero-shot cloning for the reply. All local except one Gemini API call per command. Runs in about 6 GB VRAM idle.
>
> **[Novelty]** Two things aren't in any tutorial I found. First: I fine-tuned Qwen 2.5 1.5B with rank-16 LoRA on a hand-built bilingual dataset of 508 examples specifically to rewrite skill output in a consistent formal voice — token accuracy 93.5%, eval loss 0.256. Second: instead of asking the user for a voice sample, the project auto-generates two reference clips (one per language) from Microsoft's edge-tts and clones from those on every call, so the voice identity never drifts.
>
> **[Evidence]** 16 tests pass in a second. The fine-tune ran end-to-end on my RTX 3060 in 6 minutes 24 seconds. Full demo takes 30 seconds if you want to see it live now. Three clean commits, MIT-licensed, on my public GitHub.
>
> **[Ask]** Where do you want me to open the code first — the dispatcher, the training script, or the live loop?

---

## Evidence Matrix — good vs bad examples

An evidence matrix maps every claim in the pitch to a specific artifact. This is the single most useful defense prep document.

### ❌ Weak example

| Claim | Evidence |
|---|---|
| It works | it works |
| Fine-tuned a model | I have the notebook |
| Handles two languages | tested it |

Nothing here is a pointer. "It works" cannot be verified.

### ✅ Strong example

| Claim (from the pitch) | Concrete evidence | How the examiner verifies |
|---|---|---|
| "Bilingual, Russian and English" | STT auto-detects; LLM prompt in `config.py:25-31`; 4 seed dataset files split RU/EN | Point to the code; run `python main.py` and speak RU |
| "Runs locally on my 3060" | `torch.cuda.get_device_name(0)` returns "NVIDIA GeForce RTX 3060"; VRAM check during a full turn | Live GPU-Z / task manager reading |
| "Wake-to-speaker ~1.6 s" | Timed on Day 24 with 20 samples; median 1.62 s (wake reset → first TTS sample) | Log with 20 timestamped runs |
| "2 lines to add a skill" | `jarvis/dispatcher.py` `SKILLS` dict + `TOOL_SCHEMAS` list | Point to file; add a fake skill live in 30 s |
| "Fine-tune converges" | Trainer log: eval_loss 0.256 at epoch 2 (best model), 93.5% token accuracy | Show `models/jarvis-lora/trainer_state.json` |
| "Consistent voice per language" | `assets/ref_en.wav` and `ref_ru.wav` are the only references OmniVoice ever sees | Play both clips; play three consecutive TTS outputs to show identity is stable |
| "16 tests all green" | `pytest tests/` in venv | Run it live |
| "Reproducible from clean install" | Verified on fresh Python 3.11 venv on Day 24; documented gotchas in README Troubleshooting | Delete venv, run setup, run demo |
| "One-line license fix from commercial" | OmniVoice is CC-BY-NC; other components are permissive; LICENSE NOTICE spells this out | Show LICENSE + README |

**Rule:** if you can't put a file path and a line number, it's not evidence. It's a hope.

---

## Anti-patterns to avoid

1. **"It uses AI"** — every project uses AI. Say *what* — the model name, the parameter count, the training method.
2. **"State of the art"** — never say this unless you can cite a benchmark and a leaderboard row.
3. **"Works in production"** — a demo on your laptop is not production. Say "runs locally, reproducibly."
4. **"Trained on a big dataset"** — 508 rows is not big. Own it: "508 curated bilingual examples specifically for this style task."
5. **Passive voice.** "The model was trained" — no. "I trained the model" or "I ran a 6-minute LoRA fine-tune." Verbs, not nouns.
6. **Screenshots without captions.** Every screenshot needs one sentence explaining what to look at.
