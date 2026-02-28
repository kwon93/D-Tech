import asyncio

from config import settings
from features.interview.domain.llm_port import LLMPort


class GeminiProvider(LLMPort):
    def __init__(self):
        from google import genai
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._genai = genai

    async def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        return await asyncio.to_thread(self._chat_sync, system_prompt, history, json_mode)

    def _chat_sync(self, system_prompt: str, history: list[dict], json_mode: bool) -> str:
        from google.genai import types

        contents = [
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
            contents=contents,
            config=config,
        )
        if not response.text:
            raise ValueError("Gemini로부터 빈 응답을 받았습니다.")
        return response.text