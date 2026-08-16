"""Gemini LLM wrapper — takes user text, returns either a tool call or a spoken reply.

Uses Google's `google-genai` SDK with function calling. The tool schemas
come from jarvis.dispatcher.TOOL_SCHEMAS.
"""
# Роутинг команд через Gemini API
import os
from dataclasses import dataclass

from google import genai
from google.genai import types

import config
from jarvis.dispatcher import TOOL_SCHEMAS


@dataclass
class LLMResult:
    # Результат вызова LLM
    tool_name: str | None      # если Gemini выбрал скилл
    tool_args: dict | None
    text: str | None           # если просто ответ текстом


class LLM:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Ключ обязателен — иначе крах
            raise RuntimeError("GEMINI_API_KEY not set. Copy .env.example -> .env")
        self.client = genai.Client(api_key=api_key)
        # Оборачиваем схемы скиллов в формат Gemini
        self.tools = types.Tool(function_declarations=TOOL_SCHEMAS)
        self.gen_config = types.GenerateContentConfig(
            tools=[self.tools],
            system_instruction=config.LLM_SYSTEM_PROMPT,
            temperature=0.2,   # детерминированнее
        )

    def call(self, user_text: str) -> LLMResult:
        """Send user_text to Gemini. Return the tool call (or plain text)."""
        # Один запрос — один ответ
        resp = self.client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=user_text,
            config=self.gen_config,
        )

        # Ищем function_call в ответе
        for part in resp.candidates[0].content.parts:
            fc = getattr(part, "function_call", None)
            if fc and fc.name:
                return LLMResult(tool_name=fc.name,
                                 tool_args=dict(fc.args or {}),
                                 text=None)

        # Нет вызова — просто текст
        text = (getattr(resp, "text", None) or "").strip()
        return LLMResult(tool_name=None, tool_args=None,
                         text=text or "I didn't understand.")
