# Defense Question Bank

Every question I could get asked, with a prepared answer. Grouped by topic. Answers are short on purpose — read the whole answer, then stop.

---

## A. Motivation / scoping (5 questions)

**Q1 — Why voice assistant specifically?**
It's the one project topic that legitimately requires four different model families (wake word, STT, LLM, TTS) plus fine-tuning, so I could hit multiple sections of the syllabus without stitching unrelated things together.

**Q2 — Why bilingual? Isn't English enough for a course project?**
Because I speak both, and because it forced a real constraint on the fine-tuning dataset. Monolingual would have been half the work and half the interest.

**Q3 — Why Windows only?**
That's the machine I have and it's the machine everyday users have. Cross-platform would have meant three volume backends and three app-launch backends. Out of scope, documented as a gap.

**Q4 — Why not just use ChatGPT with voice?**
Cloud, closed, expensive at scale, and impossible to add "open Notepad" as a native action without a plugin ecosystem I don't control. My assistant is 300 lines of Python I own end-to-end.

**Q5 — What would you change if you started over?**
Start writing the dev log on day one, not day 21. Also, I would have adopted `uv` for Python management on day one instead of hitting the Python 3.13 wheel problem on day 22.

---

## B. Architecture (7 questions)

**Q6 — Walk me through what happens between "Hey Jarvis" and hearing the response.**
Mic frames stream into openWakeWord; on trigger the buffer resets and the mic switches into 5-second record mode. faster-whisper transcribes with auto language detection. The text plus the 13 tool schemas go to Gemini; Gemini returns either a function call or plain text. The dispatcher calls the matching Python function, which returns a short raw string. If the LoRA stylizer is loaded, Qwen 1.5B rewrites the string in a formal voice. OmniVoice clones from the language-appropriate reference and produces WAV. sounddevice plays it. Loop repeats.

**Q7 — Why the dispatcher pattern?**
Because I want adding a skill to be *two lines*, not a subclass. A dict lookup plus a JSON schema list is the smallest thing that could possibly work, and it's what shipped.

**Q8 — Why Gemini and not a local LLM?**
Bandwidth economy. One 200-token round trip per command is nothing. A local 7 B model would eat ~5 GB of VRAM I need for the stylizer and TTS. When Gemini rate-limits me, I already have the `LLM` class as an abstraction — swap to `llama-cpp-python` behind the same interface.

**Q9 — Why OmniVoice specifically?**
Zero-shot cloning with a 3–10 second reference, ~2.5 GB VRAM in fp16, works on Windows, permissive-enough for course use (CC-BY-NC). XTTS-v2 was ~9 GB, wouldn't fit alongside Qwen.

**Q10 — Why the stylizer at all? Isn't Gemini's response already good?**
Gemini's response is text. The stylizer specifically enforces "formal, ≤20 words, 'sir'/'сэр', match input language." It also lets me use small skill outputs like "It is 14:23" and get "It is 14:23, sir." consistently instead of Gemini's varying phrasings.

**Q11 — Why LoRA and not full fine-tuning?**
1.5B params full-tune wouldn't fit on my 3060 in bf16. LoRA rank 16 trains ~18 M params (~1.18% of the model), fits in ~6 GB VRAM, adapter is 74 MB, done in 6 minutes.

**Q12 — Why keep the wake word threshold at 0.55?**
0.5 fired on unrelated words like "gervais" during background music. 0.6+ started to miss my own "Hey Jarvis." 0.55 is where I landed after a day of testing.

---

## C. Fine-tuning (6 questions)

**Q13 — How did you build the dataset?**
Four hand-written JSONL seed files (~360 rows total) covering personality and styling in both languages. Then templated augmentation: 13 apps × open/close × 2 langs, volume levels, CPU/mem pairs, battery states. Dedup by (user, assistant) pair. 90/10 split with `seed=42`. 508 train, 56 val.

**Q14 — Isn't 508 rows too small?**
For a full pretrain, yes. For a *style* adapter learning to say "sir" and stay under 20 words, no. The task is narrow. Loss curve confirms — it converges cleanly and the eval token accuracy is 93.5%.

**Q15 — How did you evaluate?**
Two ways: quantitatively, TRL's eval loss on the 56-row held-out val split; qualitatively, on Day 19 I ran 40 held-out commands through both the base Qwen and the fine-tuned adapter and scored my preference blind. Fine-tuned won 32 of 40.

**Q16 — Why nf4 4-bit and not int8?**
Both fit. nf4 is Tim Dettmers's recommendation as of bitsandbytes 0.43+ and empirically gives lower perplexity than int4 at the same memory footprint. int8 would have been fine too but slower.

**Q17 — Show me the loss curve.**
`models/jarvis-lora/trainer_state.json` has every logged step. Eval at epoch 1: 0.259, epoch 2: 0.256 (best, loaded at end), epoch 3: 0.261 (mild overfitting starting).

**Q18 — What's `paged_adamw_8bit` and why?**
An 8-bit variant of AdamW with CPU offload for optimizer states — saves ~2 GB of VRAM vs regular AdamW. Necessary because with the base model, LoRA weights, gradients, and the OmniVoice test I sometimes ran alongside, I was VRAM-tight.

---

## D. Voice cloning (5 questions)

**Q19 — Why fixed reference clips instead of asking the user?**
Onboarding friction. The original design required the user to drop `jarvis_10s.wav` in the assets folder or the whole app crashed on startup. Bad. The auto-generated refs mean the project runs out of the box.

**Q20 — Why two clips, not one universal?**
OmniVoice clones *timbre*, but pronunciation and prosody are language-dependent. An English reference produces awkward stress patterns on Russian text. Two refs = one per language, consistent within each.

**Q21 — What if I want a different voice?**
Edit `REF_EN_VOICE` and `REF_RU_VOICE` in `generate_ref_voices.py` (pick from `edge-tts --list-voices`), re-run the script. Two lines, one command, done.

**Q22 — Why edge-tts and not just record yourself?**
Reproducibility. Anyone cloning the repo gets the same voice with a single command; no "here's a WAV file, hope it works." Also, edge-tts voices are free, high-quality, and no rights issues.

**Q23 — Is this ethically fine?**
The reference voices are AI-generated Microsoft neural voices, not any real person. If a user drops in a real person's clip, they own that decision. Documented in `assets/README.md` under Legal.

---

## E. Engineering hygiene (5 questions)

**Q24 — What tests do you have?**
16 tests: 6 for the dispatcher (unknown-tool handling, schema/skills alignment, kwarg passthrough, exception wrapping), 3 for web skills (URL construction with `monkeypatch`), 4 for system skills (return-format regexes), 3 for app skills (aliases + mocked subprocess). Run in ~1 s, no GPU, no network.

**Q25 — Why so few tests?**
Because the surface I can meaningfully unit-test *is* the pure-Python skills and dispatcher. The wake word, STT, LLM, and TTS are all model calls — integration tests would need audio hardware or paid APIs. I chose depth on the small surface over breadth of shallow tests.

**Q26 — How reproducible is the training?**
Every random source has a fixed seed. Same seed → same train/val split. Same base model. Same LoRA hyperparameters in `train_lora.py`. On my machine it produces the same adapter to within numerical precision.

**Q27 — What's your git hygiene?**
Three focused commits, each with a subject line and a body explaining the *why*. Nothing else in the tree — no dead code, no half-refactors. `.env`, `models/`, and `.venv/` are ignored.

**Q28 — CI?**
None currently. Explicit gap — would be a GitHub Actions job running `pytest tests/` on push, ~30 seconds. Not shipped because the tests already run locally in one second.

---

## F. Edge cases and honest failure modes (5 questions)

**Q29 — What breaks if the internet drops?**
Wake word, STT, and stylizer keep working — all local. Gemini call fails, so no skill routing. TTS keeps working — OmniVoice is local. So Jarvis would hear you, transcribe, but be unable to route. I don't currently have a fallback; a local intent classifier would be the fix.

**Q30 — What if Gemini rate-limits me during the demo?**
Free tier is 15 req/min. I've hit it once. Recovery: wait 30 seconds. The `LLM` class is abstracted specifically so I could swap in `llama-cpp-python` behind it for offline resilience.

**Q31 — What if someone else in the room says "Jarvis"?**
It fires. openWakeWord is speaker-independent. Adding a small speaker-embedding filter is the future work item I'd prioritise if this went to production.

**Q32 — What if the WAV reference file gets corrupted?**
`generate_ref_voices.py` — one command, regenerates both refs. No manual step.

**Q33 — The stylizer sometimes runs long. What happens?**
`max_new_tokens=64` is a hard cap. Greedy decoding. Empirically outputs stay well under.

---

## Delivery notes for Q&A

- **Restate the question before answering.** Gives you 3 seconds to think and confirms you heard it right.
- **Answer, then stop.** If they want more, they'll ask. Verbose answers give more surface to attack.
- **"I don't know" is a valid answer** — better than making something up. Follow with "but I would find out by [specific method]."
- **When shown a bug, thank them and note it.** Don't apologise. "Good catch — let me pull up the file" is fine.
