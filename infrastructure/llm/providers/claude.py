import asyncio

from config import settings
from features.interview.domain.llm_port import LLMPort


class ClaudeProvider(LLMPort):
    def __init__(self):
        import anthropic
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        return await asyncio.to_thread(self._chat_sync, system_prompt, history, json_mode)

    def _chat_sync(self, system_prompt: str, history: list[dict], json_mode: bool) -> str:
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