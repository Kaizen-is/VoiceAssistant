"""Speech-to-text with faster-whisper. Multilingual, auto-detects RU vs EN."""
# Распознавание речи через Whisper
import numpy as np
from faster_whisper import WhisperModel

import config


class STT:
    def __init__(self):
        # Модель грузится один раз на GPU
        self.model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE,
        )

    def transcribe(self, audio: np.ndarray) -> tuple[str, str]:
        """Return (text, detected_language_code) e.g. ('open chrome', 'en')."""
        # Автоопределение языка (RU или EN)
        segments, info = self.model.transcribe(
            audio,
            beam_size=1,               # самый быстрый режим
            vad_filter=True,           # пропускаем тишину
            language=None,             # автоопределение языка
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text, info.language
