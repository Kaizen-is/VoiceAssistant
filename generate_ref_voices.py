"""One-shot: synthesize the two fixed reference voice clips.

Every OmniVoice generation at runtime clones from a reference clip. Using a
FIXED reference per language keeps the voice identity stable across every
response. Run this once:

    python generate_ref_voices.py

Produces:
    assets/ref_en.wav  — clone target for English responses
    assets/ref_ru.wav  — clone target for Russian responses

The exact text of each clip is baked into config.py as REF_TEXT_EN/REF_TEXT_RU
so OmniVoice does not have to auto-transcribe it every call.
"""
# Генератор фиксированных эталонных клипов
import asyncio
import io
from pathlib import Path

# Windows CA fix — Microsoft's TTS endpoint hits the same SSL issue
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import av
import edge_tts
import numpy as np
import soundfile as sf

ASSETS = Path(__file__).parent / "assets"

# --- Reference clips: text + voice + output file --- #
# EN — короткая формальная фраза. British male voice, close to Iron-Man's Jarvis.
REF_EN_TEXT = "Hello sir. All systems are online. I am at your service."
REF_EN_VOICE = "en-GB-RyanNeural"

# RU — та же идея, тот же диктор по духу (мужской, спокойный).
REF_RU_TEXT = "Здравствуйте, сэр. Все системы работают исправно. Я к вашим услугам."
REF_RU_VOICE = "ru-RU-DmitryNeural"


async def _synth_mp3(text: str, voice: str) -> bytes:
    # Стримим MP3 из Microsoft-эндпоинта, склеиваем в один буфер
    communicate = edge_tts.Communicate(text, voice)
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


def _mp3_to_wav(mp3_bytes: bytes, out_path: Path) -> None:
    # Декодируем MP3 через PyAV (ffmpeg-биндинги) и пишем моно 24 кГц
    container = av.open(io.BytesIO(mp3_bytes))
    stream = container.streams.audio[0]

    frames: list[np.ndarray] = []
    for frame in container.decode(stream):
        arr = frame.to_ndarray()
        frames.append(arr)

    audio = np.concatenate(frames, axis=1)  # (channels, samples)
    if audio.shape[0] > 1:                  # → mono
        audio = audio.mean(axis=0, keepdims=True)
    audio = audio.squeeze(0)

    # Приводим к float32 в [-1, 1]
    if np.issubdtype(audio.dtype, np.integer):
        audio = audio.astype(np.float32) / np.iinfo(audio.dtype).max
    else:
        audio = audio.astype(np.float32)

    sf.write(str(out_path), audio, stream.rate, subtype="PCM_16")
    print(f"  wrote {out_path.name}  ({len(audio) / stream.rate:.2f} s @ {stream.rate} Hz)")


async def main() -> None:
    ASSETS.mkdir(exist_ok=True)

    print(f"Synthesizing EN reference with {REF_EN_VOICE}...")
    mp3 = await _synth_mp3(REF_EN_TEXT, REF_EN_VOICE)
    _mp3_to_wav(mp3, ASSETS / "ref_en.wav")

    print(f"Synthesizing RU reference with {REF_RU_VOICE}...")
    mp3 = await _synth_mp3(REF_RU_TEXT, REF_RU_VOICE)
    _mp3_to_wav(mp3, ASSETS / "ref_ru.wav")

    print("\nDone. Reference clips saved. They are the fixed voice identity —")
    print("every runtime TTS call clones from one of them, keeping the voice consistent.")


if __name__ == "__main__":
    asyncio.run(main())
