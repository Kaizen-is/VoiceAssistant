# Rubric — with Self-Assessment

Standard capstone rubric, adapted for a speech-and-LLM project. Every criterion gets a self-grade with justification.

Scale: 0 (missing) · 1 (started) · 2 (partial) · 3 (complete) · 4 (exceeds baseline)

---

## A. Problem definition and motivation (weight ~10%)

| Criterion | Weight | Self-grade | Justification |
|---|---|---|---|
| Clearly stated problem, not "I want to build X" | 5 | **3** | "Bilingual local voice assistant, Windows, extensible in 2 lines" — see `WORKSHEET.md` §1. Concrete gap identified. |
| Explanation of why it matters | 3 | **3** | Cloud-only, English-only, closed-source landscape called out; personal use case is honest. |
| Stakeholders and success criteria named | 2 | **2** | Success = "I can say a command and it works, and someone else can add a new one without asking me." Not a formal SLA. |

## B. Technical implementation (weight ~40%)

| Criterion | Weight | Self-grade | Justification |
|---|---|---|---|
| Working end-to-end system | 10 | **4** | Full loop verified; `pytest` green; live demo works; three git commits show iteration. |
| Model or algorithm choice justified | 8 | **3** | Every stage's model has a "why" in `DEV_LOG_25_DAYS.md` (Days 2–4). Alternatives were considered (Vosk, XTTS, Porcupine) and rejected with reasons. |
| Correct use of framework(s) | 8 | **3** | PyTorch, HuggingFace transformers, peft, trl, faster-whisper, openWakeWord all used idiomatically. TRL API drift caught and fixed. |
| Reproducibility (fixed seeds, pinned versions) | 8 | **3** | `seed=42` in dataset builder and trainer; `requirements.txt` pinned; Python 3.11 constraint documented. |
| Code quality (structure, naming, no dead code) | 6 | **3** | One concern per module; no stubs; no TODOs; comments only where the "why" is non-obvious. |

## C. Fine-tuning / training work (weight ~20%)

| Criterion | Weight | Self-grade | Justification |
|---|---|---|---|
| Dataset construction documented | 5 | **3** | 4 hand-written seed files + templated augmentation, dedup, 90/10 split. Every step in `data/build_dataset.py`. |
| Training pipeline runnable | 5 | **4** | `python train_lora.py` — one command, no manual steps. |
| Metrics reported honestly | 5 | **3** | Eval loss 0.256, token accuracy 93.5%. Not benchmarked against a baseline, but qualitatively verified with a 40-command A/B on Day 19. |
| Model / adapter shipped | 5 | **3** | Adapter (74 MB) is regenerable but git-ignored. Ship the training script, not the artifact. |

## D. Presentation and defense (weight ~20%)

| Criterion | Weight | Self-grade | Justification |
|---|---|---|---|
| Clear slides (structure, no wall of text) | 5 | **3** | `presentation.html` — 13 slides, at most one main point per slide. |
| Live demo prepared | 5 | **3** | Startup ~3 s, five demo commands memorised, fallback if Gemini rate-limits. |
| Pitch (30-s and 3-min) rehearsed | 5 | **3** | Written out in `PITCH_AND_EVIDENCE.md`. Strong vs weak side by side. |
| Q&A preparation | 5 | **3** | 30+ questions in `defense_templates/defense_question_bank.md` with answers. |

## E. Reflection and honesty (weight ~10%)

| Criterion | Weight | Self-grade | Justification |
|---|---|---|---|
| Named gaps and limitations | 4 | **3** | 5 explicit gaps in `WORKSHEET.md` §4; risks in §6. |
| Explained what was hardest | 3 | **3** | Wake-word self-trigger, SSL cert issue, TRL API drift — all in `DEV_LOG_25_DAYS.md`. |
| Would-change-in-hindsight statement | 3 | **3** | "Start writing the log on Day 1, not Day 21." — Day 25 meta section. |

---

## Aggregate

Weighted mean: **~3.1 / 4** (equivalent to a solid pass with room to push toward distinction).

Where I'd expect to lose points:
- **No formal benchmark for the stylizer.** 40-command self-evaluation is qualitative; a proper held-out evaluation with a second human rater would strengthen this.
- **No CI.** `pytest tests/` runs locally in a second, but there's no GitHub Actions workflow.
- **Windows-only.** If the rubric expects cross-platform, this loses points.

Where I'd expect to score high:
- **End-to-end system that actually runs.** Many capstone projects show a notebook or a model but not a whole pipeline.
- **Real engineering decisions with real reasoning** — every model choice has a "why", not just "the tutorial used this."
- **Documentation depth.** Log, worksheet, evidence matrix, question bank, and this rubric — all present and non-trivial.

---

## What "exceeds" would look like

To move from 3 → 4 on any B/C row:
- **B.reproducibility:** add a GitHub Actions workflow that runs `pytest` on push, and a `.python-version` file for `pyenv`.
- **C.metrics:** add a script `eval_stylizer.py` that runs the fine-tuned adapter against 100 held-out raw strings, scores by a second LLM judge, and prints a comparison table vs the base model.
- **B.working system:** a screen-recording of a full demo, timestamped and embedded in the README.
