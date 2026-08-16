"""Entry point. Runs the wake-word → STT → LLM → skill → TTS loop forever."""
# Точка входа проекта

# Route SSL through the OS trust store — fixes HF/Gemini cert issues on some Windows setups
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from dotenv import load_dotenv
load_dotenv()   # читаем .env

import config
from jarvis.wake_word import WakeWordListener
from jarvis.stt import STT
from jarvis.llm import LLM
from jarvis.tts import TTS
from jarvis.dispatcher import dispatch
from jarvis.audio_io import record_seconds, play


def main() -> None:
    print("Loading models (first run downloads weights, ~2 GB)...")
    # Загружаем все модели один раз
    wake = WakeWordListener()
    stt = STT()
    llm = LLM()
    tts = TTS()

    # Стилизатор — опциональный, работает если обучен адаптер
    stylizer = None
    if config.STYLIZER_ENABLED:
        try:
            from jarvis.stylize import Stylizer
            stylizer = Stylizer()
            print("Response stylizer loaded (Qwen + Jarvis LoRA).")
        except FileNotFoundError as e:
            # Мягкий откат — говорим сырой ответ
            print(f"Stylizer disabled: {e}")

    print("\nJarvis is ready. Say 'Hey Jarvis' to give a command.\n")

    # Основной цикл — работает бесконечно
    while True:
        try:
            wake.listen()   # блокируется до слова "Jarvis"
            print("Wake word detected. Listening for command...")

            # Запись команды после пробуждения
            audio = record_seconds(config.COMMAND_RECORD_SECONDS, config.SAMPLE_RATE)
            text, lang = stt.transcribe(audio)
            if not text:
                print("(nothing heard)\n")
                continue
            print(f"[{lang}] Heard: {text}")

            # Gemini решает какой скилл вызвать
            result = llm.call(text)
            if result.tool_name:
                print(f"Tool: {result.tool_name}({result.tool_args})")
                raw = dispatch(result.tool_name, result.tool_args)
            else:
                raw = result.text
            print(f"Raw: {raw}")

            # Переписываем в голосе Джарвиса
            response = stylizer.stylize(raw) if stylizer else raw
            print(f"Say: {response}\n")

            # Синтез и воспроизведение
            wav, sr = tts.speak(response)
            play(wav, sr)

        except KeyboardInterrupt:
            print("\nGoodbye.")
            break
        except Exception as e:
            print(f"[error] {e}\n")


if __name__ == "__main__":
    main()
