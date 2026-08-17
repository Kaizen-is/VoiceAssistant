# README FIRST — Defense Pack for JarvisAssistant

Read these files in order. Each takes 5–10 minutes.

## Order

1. **[README_FIRST.md](README_FIRST.md)** — you are here. 90-second overview of what's in this pack and why.
2. **[DEV_LOG_25_DAYS.md](DEV_LOG_25_DAYS.md)** — 25-day development log. What was built, in what order, and what got stuck. Read this first if the examiner asks *"walk me through how you built this."*
3. **[WORKSHEET.md](WORKSHEET.md)** — the unified capstone worksheet, already filled in. One page per section: problem, method, evidence, gaps, next steps. The single most compact view of the project.
4. **[presentation.html](presentation.html)** — the live presentation slides. Open in any browser (Chrome/Edge). Use `→` / `←` or `Space` / `Shift+Space` to navigate. `F` for fullscreen, `Esc` to exit. Designed to be presented in ~10 minutes, defended in another ~10.
5. **[PITCH_AND_EVIDENCE.md](PITCH_AND_EVIDENCE.md)** — a strong vs weak version of the elevator pitch, side by side. Explains why the strong one works. Same treatment for the evidence matrix.
6. **[EVIDENCE_PATHS.md](EVIDENCE_PATHS.md)** — pointers to every artifact the examiner might ask to see: dataset, training script, trained adapter, tests, live demo. One click per artifact.
7. **[defense_templates/](defense_templates/)** — five filled-in defense artifacts:
   - `defense_pitch_outline.md` — 90-second pitch structure
   - `capstone_evidence_matrix.md` — claim → evidence table
   - `defense_question_bank.md` — 30+ questions the examiner is likely to ask, with prepared answers
   - `final_action_plan.md` — what happens post-defense (limits, next steps)
   - `PROJECT_STATUS.md` — one-page status snapshot as of today
8. **[RUBRIC.md](RUBRIC.md)** — the rubric this defense is graded against, with a self-assessment for every criterion.

## Fastest possible path

If you have 15 minutes before the defense:

1. Skim **DEV_LOG_25_DAYS.md** — you'll remember every step you took.
2. Read **defense_templates/defense_pitch_outline.md** aloud once.
3. Open **presentation.html** and click through every slide once.

That covers the top 80% of what gets asked.

## Where the actual project lives

Everything in this `docs/` folder is *about* the project. The project itself is in the repo root:

- Source code: `jarvis/`, `main.py`, `config.py`, `train_lora.py`
- Dataset: `data/`
- Tests: `tests/`
- Trained LoRA adapter: `models/jarvis-lora/` (local only — 74 MB, git-ignored)
- Voice reference clips: `assets/ref_en.wav`, `assets/ref_ru.wav`
- Full setup + run instructions: root `README.md`

## Course

- Code: **EXTC4** — Self-Work Capstone
- Student: **Junior Jumanazarov**
- Repo: <https://github.com/Kaizen-is/VoiceAssistant>
- Defense date: *(fill in before printing)*
