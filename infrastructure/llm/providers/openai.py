import asyncio

from config import settings
from features.interview.domain.llm_port import LLMPort


class OpenAIProvider(LLMPort):
    def __init__(self):
        from openai import OpenAI
        self._client = OpenAI(api_key=settings.openai_api_key)

    async def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        return await asyncio.to_thread(self._chat_sync, system_prompt, history, json_mode)

    def _chat_sync(self, system_prompt: str, history: list[dict], json_mode: bool) -> str:
        messages = [{"role": "system", "content": system_prompt}] + history
        kwargs: dict = {"model": "gpt-4.1-mini", "messages": messages}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        content = self._client.chat.completions.create(**kwargs).choices[0].message.content
        if not content:
            raise ValueError("OpenAI로부터 빈 응답을 받았습니다.")
        return content