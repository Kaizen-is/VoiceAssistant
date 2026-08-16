"""OmniVoice TTS with zero-shot voice cloning from a 3–10 s reference clip."""
# Синтез речи с клонированием голоса
from pathlib import Path

import numpy as np
import torch
from omnivoice import OmniVoice

import config


class TTS:
    def __init__(self):
        # Проверяем эталонное аудио
        ref = Path(config.TTS_REF_AUDIO)
        if not ref.exists():
            raise FileNotFoundError(
                f"Reference voice not found at {ref}. "
                "Put a 3–10 s WAV clip of the target voice there (see assets/README.md)."
            )
        self.ref_audio = str(ref)
        # Модель загружается в GPU в fp16 (~2.5 ГБ VRAM)
        self.model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice",
            device_map=config.TTS_DEVICE,
            dtype=torch.float16,
        )

    def speak(self, text: str) -> tuple[np.ndarray, int]:
        """Return (audio_float32, sample_rate). Whisper auto-transcribes the ref."""
        # Клонирование голоса из эталона
        audio = self.model.generate(
            text=text,
            ref_audio=self.ref_audio,
            ref_text=None,   # OmniVoice сам распознаёт эталон
        )
        # OmniVoice возвращает батч — берём первый
        wav = audio[0] if isinstance(audio, (list, tuple)) or getattr(audio, "ndim", 0) > 1 else audio
        return np.asarray(wav, dtype=np.float32), config.TTS_OUTPUT_SR
