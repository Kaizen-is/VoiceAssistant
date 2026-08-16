# Voice reference clip

Put a **3–10 second WAV file** here named `jarvis_10s.wav`. OmniVoice will
clone this voice on every response.

## Requirements
- Format: WAV, mono preferred (stereo is auto-mixed)
- Sample rate: any (OmniVoice resamples internally)
- Duration: 3–10 seconds; ~7 s is a good sweet spot
- Content: clean speech, no music/background noise, no long silences
- Speaker: keep it consistent — one person, one language works best

## Where to get a Jarvis clip
- Rip ~7 s of dialogue from an Iron Man scene where JARVIS is speaking
  clearly (YouTube → `yt-dlp` → `ffmpeg -ss <start> -t 7 -ac 1 -ar 24000 out.wav`)
- Or record any voice you want Jarvis to sound like

Legal note: the OmniVoice model is **CC-BY-NC** — non-commercial use only.
Fine for a course project; do not ship this commercially.
