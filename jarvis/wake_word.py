"""Wake-word listener using openWakeWord's pre-trained 'hey_jarvis' model."""
# Детектор слова пробуждения
import numpy as np
from openwakeword.model import Model

import config
from jarvis.audio_io import mic_frames


class WakeWordListener:
    def __init__(self):
        # Скачиваем модели при первом запуске (идемпотентно)
        try:
            import openwakeword.utils as owutils
            owutils.download_models()
        except Exception:
            pass  # уже скачано или нет сети

        # Загружаем только "hey_jarvis" — быстрее и меньше памяти
        self.model = Model(wakeword_models=[config.WAKE_WORD_MODEL])
        self.threshold = config.WAKE_THRESHOLD
        # openWakeWord ждёт 80 мс кадры при 16 кГц = 1280 сэмплов
        self.frame_samples = int(config.SAMPLE_RATE * config.FRAME_MS / 1000)

    def listen(self) -> None:
        """Block until the wake word is heard. Returns silently on trigger."""
        # Блокируется до срабатывания
        for frame in mic_frames(self.frame_samples, config.SAMPLE_RATE):
            scores = self.model.predict(frame)
            for _key, score in scores.items():
                if score >= self.threshold:
                    # Сброс буфера — чтобы не сработать на TTS Джарвиса
                    self.model.reset()
                    return
