# Jarvis fine-tuning dataset

Purpose: teach a small local LLM (Qwen 2.5 1.5B target) to **style responses
in Jarvis's voice**. This model runs *after* the tool dispatcher — the
Gemini-side tool routing is unaffected.

## Files

| File | Rows | Purpose |
|---|---|---|
| `en_personality.jsonl` | 115 | English chit-chat in Jarvis voice |
| `ru_personality.jsonl` | 110 | Russian chit-chat in Jarvis voice |
| `en_styling.jsonl` | 69 | English raw skill output → Jarvis rephrase |
| `ru_styling.jsonl` | 68 | Russian raw skill output → Jarvis rephrase |
| `build_dataset.py` | — | Combines all 4, adds ~200 template-augmented rows, dedups, shuffles, splits 90/10 |
| `train.jsonl` | ~500 (after build) | Fine-tuning set |
| `val.jsonl` | ~55 (after build) | Held-out eval set |

## Format

Each row is a JSON object in **OpenAI messages format** — compatible with
Unsloth, TRL SFTTrainer, and most modern fine-tuning frameworks:

```json
{"messages": [
  {"role": "system",    "content": "You are Jarvis..."},
  {"role": "user",      "content": "..."},
  {"role": "assistant", "content": "..."}
]}
```

Two system prompts are used:
1. **Personality** — for direct conversation
2. **Styling** — for rewriting raw tool output in Jarvis's voice

## Build

```bash
python data/build_dataset.py
```

Output:
```
  en_personality.jsonl       115 rows
  ru_personality.jsonl       105 rows
  en_styling.jsonl            65 rows
  ru_styling.jsonl            68 rows
  seed total                 353 rows
  template-augmented         362 rows
  after dedup                ~700 rows
Wrote data/train.jsonl (~630 rows)
Wrote data/val.jsonl   (~70 rows)
```

## Extending the dataset

Two ways:

1. **Add hand-crafted rows** to any of the 4 category files — one JSON per
   line, same schema. Rerun `build_dataset.py`.
2. **Expand templates** in `build_dataset.py::augment()` — add more app
   aliases, volume steps, error patterns, times, dates.

## How this connects to the runtime

After training a LoRA adapter on `train.jsonl`, plug it into
`jarvis/stylize.py` (a new module) with a `stylize(text: str) -> str` call.
Insert it in `main.py` right after `dispatch()` returns:

```python
raw = dispatch(result.tool_name, result.tool_args)
response = stylize(raw)   # <-- Jarvis-voice rewrite
```

The base LLM (Gemini) still handles intent + tool selection. The fine-tuned
local model *only* handles voice styling. Two models, two jobs.

## License

Dataset content is CC-BY-4.0 — free to use, modify, redistribute with attribution.
