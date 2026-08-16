"""Load Qwen 2.5 1.5B + Jarvis LoRA adapter. Rewrites raw tool output
in Jarvis's voice at runtime.

Sits between dispatch() and tts.speak() in the main loop.
Falls back gracefully to the raw text if the adapter isn't trained yet.
"""
# Стилизация ответов в голосе Джарвиса
from pathlib import Path

import torch
from peft import PeftModel
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          BitsAndBytesConfig)

import config

# Системный промпт для стилизации
STYLE_SYSTEM_PROMPT = (
    "You are Jarvis. Rephrase the given system output in your characteristic voice "
    "— formal, concise, address the user as 'sir' (English) or 'сэр' (Russian). "
    "Match the language of the input. Keep it under 20 words."
)


class Stylizer:
    def __init__(self):
        # Проверяем что адаптер обучен
        adapter = Path(config.STYLIZER_ADAPTER)
        if not adapter.exists():
            raise FileNotFoundError(
                f"LoRA adapter not found at {adapter}. "
                "Run `python train_lora.py` first, or set STYLIZER_ENABLED=False in config.py."
            )

        # 4-битная квантизация — экономим VRAM
        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(config.STYLIZER_BASE)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Базовая модель + LoRA поверх
        base = AutoModelForCausalLM.from_pretrained(
            config.STYLIZER_BASE,
            quantization_config=bnb,
            device_map="auto",
        )
        self.model = PeftModel.from_pretrained(base, str(adapter))
        self.model.eval()

    def stylize(self, text: str) -> str:
        """Rewrite `text` in Jarvis's voice. Deterministic — same input → same output."""
        # Формируем промпт по шаблону чата
        messages = [
            {"role": "system", "content": STYLE_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        # Жадная генерация — стабильный голос
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=64,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Отрезаем промпт, декодируем только ответ
        gen_ids = out[0][inputs.input_ids.shape[1]:]
        return self.tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
