from abc import ABC, abstractmethod


class LLMPort(ABC):
    @abstractmethod
    async def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        """
        system_prompt: 시스템 지시문
        history: [{"role": "user"|"assistant", "content": "..."}]
        json_mode: True이면 JSON 문자열만 반환
        """
        ...
