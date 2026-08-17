# Final Action Plan — Post-Defense

What ships now, what waits, what dies.

---

## Immediately after the defense (Week 1)

- [ ] Push any last-minute defense edits to `main` on GitHub.
- [ ] Tag the current commit as `v1.0-course-submission` for the archive.
- [ ] Screen-record a 90-second demo showing wake → command → response, EN and RU. Upload to the repo README.
- [ ] Add a GitHub Actions workflow that runs `pytest tests/` on every push. ~30 lines of YAML, closes the "no CI" gap called out in the rubric self-assessment.

## Short-term follow-ups (Month 1)

- [ ] **Streaming STT.** Replace the fixed 5-second `record_seconds()` call with a VAD-driven variable-length recording. Cuts idle wait when commands are short. About a day of work.
- [ ] **Speaker filter on wake word.** Train a small speaker-embedding classifier on 50 samples of my own "Hey Jarvis." Drops false-positive rate for other people in the room from "some" to "near zero." Half a day.
- [ ] **Local LLM fallback.** Behind the existing `LLM` class interface, add `llama-cpp-python` as a fallback for when Gemini rate-limits or the network is down. About a day.
- [ ] **Metric script for the stylizer.** `eval_stylizer.py` that runs 100 held-out raw strings through both base Qwen and the fine-tuned adapter, scores by a second LLM judge, prints a comparison table. Formal evaluation to move the rubric self-grade from 3 to 4. Half a day.

## Medium-term (Quarter 1)

- [ ] **Multi-turn conversation.** Add a per-session context store so follow-up questions work ("what's the weather" → "and tomorrow?"). Requires prompt-template rewrite and a small state machine. About 3 days.
- [ ] **Skill expansion.** Calendar (Outlook COM), email (SMTP send), file search (Everything CLI), Spotify control (spotipy). Each is one skill file plus two dispatcher lines — the ceiling is API plumbing, not framework. ~1 day per skill.
- [ ] **Cross-platform.** Port `pycaw` calls to a platform-abstracted backend (Linux: pactl / pipewire; macOS: osascript). App launch same treatment. About a week if I ever leave Windows.

## Long-term / speculative (Quarter 2+)

- **Home Assistant integration.** JarvisAssistant as an HA voice satellite — control the smart-home stack via the same dispatcher pattern. Feasible; several days of MQTT/websocket plumbing.
- **Personal-only wake word.** Train a personalised `hey_junior` model from scratch using openWakeWord's training pipeline. Would replace speaker filtering. Bigger project.
- **Multi-language support beyond RU/EN.** OmniVoice supports many languages; Qwen tokenizer covers a lot. Would need another round of hand-written seed data per new language.

## Explicit non-goals

- **Mobile app.** Different form factor, different constraints, would be a separate project.
- **Commercial productisation.** OmniVoice is CC-BY-NC. Swapping the TTS backend is the migration path if this ever needs to be commercial.
- **Fully offline everything.** Gemini stays as long as it's free and fast. A truly offline mode is a fallback, not a headline feature.
- **Native GUI.** CLI is the demo surface. A GUI adds surface without adding function.

## Personal takeaways to carry into the next project

1. **Start the dev log on day one.** Not day 21.
2. **Pin Python early.** `.python-version` file + `uv` from the first commit.
3. **Ship the dependency shim before it bites.** `truststore.inject_into_ssl()` should have been in place from day one on this machine.
4. **Keep the dispatcher pattern.** Two-line skill addition is the single design decision I would replicate in every future project of similar shape.
5. **Documentation depth pays off in the defense.** The 25-day log, evidence matrix, and question bank took ~4 hours to write on the last day; they change how confidently I can walk into the defense.

---

## Success criteria for this action plan

By the end of Month 1, the repo should have:
- CI green on `main`
- A 90-second demo video in the README
- Streaming STT
- A speaker filter on the wake word
- A local LLM fallback path
- The formal stylizer eval script + a comparison table

If those five things ship, this project graduates from "course submission" to "hobby project I actually use."
