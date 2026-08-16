"""Microphone recording and speaker playback helpers."""
# Работа с микрофоном и динамиками
import numpy as np
import sounddevice as sd


def record_seconds(seconds: float, sample_rate: int = 16_000) -> np.ndarray:
    """Blocking record for a fixed duration. Returns float32 mono in [-1, 1]."""
    # Синхронная запись фиксированной длины
    audio = sd.rec(int(seconds * sample_rate),
                   samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()   # ждём окончания записи
    return audio.flatten()


def play(audio: np.ndarray, sample_rate: int) -> None:
    """Blocking playback of mono float32 audio."""
    # Воспроизведение через системный динамик
    sd.play(audio, samplerate=sample_rate)
    sd.wait()


def mic_frames(frame_samples: int, sample_rate: int = 16_000):
    """Generator yielding int16 mic frames of `frame_samples` samples each.
    Used by the wake-word detector for continuous listening."""
    # Непрерывный поток кадров для детектора
    q = []

    def _cb(indata, frames, time_info, status):
        # Колбэк sounddevice — кладём кадр в очередь
        q.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, channels=1,
                        dtype="int16", blocksize=frame_samples, callback=_cb):
        buf = np.zeros((0,), dtype=np.int16)
        while True:
            # Ждём пока не наберётся кадр
            while not q:
                sd.sleep(10)
            buf = np.concatenate([buf, q.pop(0).flatten()])
            while len(buf) >= frame_samples:
                yield buf[:frame_samples]
                buf = buf[frame_samples:]
