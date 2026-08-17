"""OmniVoice TTS with zero-shot voice cloning from a fixed per-language reference."""
# Синтез речи с фиксированным эталонным клипом на каждый язык
from pathlib import Path

import numpy as np
import torch
from omnivoice import OmniVoice

import config


class TTS:
    def __init__(self):
        # Проверяем что оба эталонных клипа сгенерированы
        missing = [str(p) for p in (config.TTS_REF_EN, config.TTS_REF_RU)
                   if not Path(p).exists()]
        if missing:
            raise FileNotFoundError(
                f"Reference voice clips not found: {missing}. "
                "Run `python generate_ref_voices.py` first."
            )
        # Словарь язык → (файл, текст) — выбираем в speak()
        self._refs = {
            "en": (str(config.TTS_REF_EN), config.TTS_REF_TEXT_EN),
            "ru": (str(config.TTS_REF_RU), config.TTS_REF_TEXT_RU),
        }
        # Модель загружается в GPU в fp16 (~2.5 ГБ VRAM)
        self.model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice",
            device_map=config.TTS_DEVICE,
            dtype=torch.float16,
        )

    def speak(self, text: str, lang: str = "en") -> tuple[np.ndarray, int]:
        """Return (audio_float32, sample_rate). `lang` picks the reference clip."""
        # По языку берём соответствующий эталон, английский — дефолт
        ref_audio, ref_text = self._refs.get(lang, self._refs["en"])
        audio = self.model.generate(
            text=text,
            ref_audio=ref_audio,
            ref_text=ref_text,      # точный текст эталона — быстрее и точнее
        )
        # OmniVoice может вернуть батч — берём первый элемент
        wav = audio[0] if isinstance(audio, (list, tuple)) or getattr(audio, "ndim", 0) > 1 else audio
        return np.asarray(wav, dtype=np.float32), config.TTS_OUTPUT_SR
