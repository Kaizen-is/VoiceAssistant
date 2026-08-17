# Defense Pitch Outline — 90 seconds

Read this out loud once before the defense. Time it — should land at 90 seconds ± 10.

---

**[0:00 – 0:15] Hook**

JarvisAssistant is a bilingual voice assistant that lives entirely on my RTX 3060. Wake to speaker in about 1.6 seconds. It answers in Russian or English with the same voice identity because the TTS clones from a fixed reference clip per language.

**[0:15 – 0:35] Problem**

Every mainstream voice assistant is cloud-only, English-first, and closed. A bilingual Windows user who wants to open Chrome by voice AND own the code has no good option. So I built one.

**[0:35 – 1:00] Solution**

Five stages, all wired by one file. Wake word from openWakeWord. Speech to text from faster-whisper. Intent from Gemini function calling — 13 tool schemas, one API call per command. Skills are plain Python functions. Text to speech from OmniVoice with zero-shot voice cloning. And a Qwen 1.5B LoRA I fine-tuned on 508 examples that rewrites every skill output in a formal voice before it hits TTS.

**[1:00 – 1:20] Evidence and novelty**

Two things aren't in any tutorial. First, the fine-tune is bilingual by construction — every training row has an RU and EN counterpart. Eval loss 0.256, token accuracy 93.5%, six minutes on my 3060. Second, the voice identity problem: instead of asking the user for a voice sample, the project auto-generates two references with edge-tts and clones from those forever. Voice never drifts.

**[1:20 – 1:30] Ask**

16 tests pass in a second. Three commits, MIT-licensed, on my GitHub. Where do you want me to open the code first — the dispatcher, the training script, or the live loop?

---

## Delivery notes

- **Speak slower than feels natural.** ~140 words per minute, not 180. The above is ~200 words = ~85 seconds at 140 wpm.
- **Hands: relaxed on the podium, or one holding a pen.** Not in pockets, not gesticulating.
- **Eyes: rotate through 3 people in the room.** ~5 seconds each. Do not read from the slides.
- **On "1.6 seconds" and "93.5%": pause half a beat before saying the number.** These are the two memorable numbers; give them space to land.
- **Do NOT apologise.** "This is a small project" or "I know it's not perfect" — cut. State what it is.
- **End with a question, not a "thanks."** The examiner is now committed to picking one of the three code paths, which gives you agency over the first 5 minutes of Q&A.

## Backup one-liner (for the elevator)

> A bilingual local voice assistant for Windows with a fine-tuned Qwen stylizer and language-consistent voice cloning, extensible in two lines of Python per new command.

## What NOT to say

- "It uses AI." — every project uses AI. Name the model.
- "State of the art." — you don't have a leaderboard.
- "Basically." — verbal hedge. Cut.
- "As you can see" — they may not. Point.
- "Sort of" — pick a side.
