# Voice reference clips

Two fixed reference clips live here — one per language. Every runtime TTS
call clones from one of them (English response → `ref_en.wav`, Russian
response → `ref_ru.wav`), which keeps the voice identity stable across
every generation.

## Files
- `ref_en.wav` — English reference (British male, `en-GB-RyanNeural`)
- `ref_ru.wav` — Russian reference (Russian male, `ru-RU-DmitryNeural`)

## Generating them

Both are produced by a one-shot script that hits Microsoft's edge-tts
endpoint:

```powershell
python generate_ref_voices.py
```

The exact text of each clip is baked into `config.py` (`TTS_REF_TEXT_EN` /
`TTS_REF_TEXT_RU`) so OmniVoice does not have to auto-transcribe them at
runtime.

## Swapping voices

Prefer a different-sounding Jarvis? Pick another edge-tts voice from
`edge-tts --list-voices`, update `REF_EN_VOICE` / `REF_RU_VOICE` in
`generate_ref_voices.py`, and re-run the script. The clips overwrite in
place; no config change needed unless you also change the reference text.

## Legal

OmniVoice is **CC-BY-NC** — non-commercial use only. Fine for a course
project; do not ship this commercially. The edge-tts endpoint is a
Microsoft Azure Cognitive Services free tier, subject to their terms.
