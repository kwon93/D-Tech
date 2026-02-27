"""
LLM Provider 추상화 레이어.

.env에 설정된 키에 따라 자동으로 프로바이더를 선택합니다:
  GEMINI_API_KEY    → GeminiProvider  (gemini-2.5-flash)
  OPENAI_API_KEY    → OpenAIProvider  (gpt-4.1-mini)
  ANTHROPIC_API_KEY → ClaudeProvider  (claude-haiku-4-5-20251001)

공통 history 포맷:
  [{"role": "user" | "assistant", "content": "..."}]
"""

import os
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        """
        system_prompt: 시스템 지시문
        history: [{"role": "user"|"assistant", "content": "..."}]
        json_mode: True이면 JSON 문자열만 반환
        """
        ...


class GeminiProvider(LLMProvider):
    def __init__(self):
        from google import genai
        self._client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self._genai = genai

    def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        from google.genai import types

        gemini_contents = [
            types.Content(
                role="model" if m["role"] == "assistant" else "user",
                parts=[types.Part(text=m["content"])],
            )
            for m in history
        ]
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            response_mime_type="application/json" if json_mode else "text/plain",
        )
        response = self._client.models.generate_content(
            model="gemini-2.5-flash",
            contents=gemini_contents,
            config=config,
        )
        if not response.text:
            raise ValueError("Gemini로부터 빈 응답을 받았습니다.")
        return response.text


class OpenAIProvider(LLMProvider):
    def __init__(self):
        from openai import OpenAI
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        messages = [{"role": "system", "content": system_prompt}] + history
        kwargs: dict = {"model": "gpt-4.1-mini", "messages": messages}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        content = self._client.chat.completions.create(**kwargs).choices[0].message.content
        if not content:
            raise ValueError("OpenAI로부터 빈 응답을 받았습니다.")
        return content


class ClaudeProvider(LLMProvider):
    def __init__(self):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        system = system_prompt
        if json_mode:
            system += "\n\nJSON 형식으로만 응답하세요. 마크다운 코드블록 없이 순수 JSON만 출력하세요."

        response = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=history,
        )
        text = response.content[0].text
        if not text:
            raise ValueError("Claude로부터 빈 응답을 받았습니다.")
        return text


def get_provider() -> LLMProvider:
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

    if gemini_key:
        return GeminiProvider()
    if openai_key:
        return OpenAIProvider()
    if anthropic_key:
        return ClaudeProvider()
    raise RuntimeError(
        "API 키가 없습니다. .env 파일에 다음 중 하나를 설정하세요:\n"
        "  GEMINI_API_KEY=...\n"
        "  OPENAI_API_KEY=...\n"
        "  ANTHROPIC_API_KEY=..."
    )
