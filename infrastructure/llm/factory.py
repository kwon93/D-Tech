from functools import lru_cache

from config import settings
from features.interview.domain.llm_port import LLMPort
from infrastructure.llm.failover import FailoverLLMProvider


@lru_cache(maxsize=1)
def create_provider() -> LLMPort:
    providers: list[tuple[str, LLMPort]] = []

    if settings.gemini_api_key:
        from infrastructure.llm.providers.gemini import GeminiProvider
        providers.append(("gemini", GeminiProvider()))
    if settings.openai_api_key:
        from infrastructure.llm.providers.openai import OpenAIProvider
        providers.append(("openai", OpenAIProvider()))
    if settings.anthropic_api_key:
        from infrastructure.llm.providers.claude import ClaudeProvider
        providers.append(("claude", ClaudeProvider()))
    if providers:
        if len(providers) == 1:
            return providers[0][1]
        return FailoverLLMProvider(providers)
    raise RuntimeError(
        "API 키가 없습니다. .env 파일에 다음 중 하나를 설정하세요:\n"
        "  GEMINI_API_KEY=...\n"
        "  OPENAI_API_KEY=...\n"
        "  ANTHROPIC_API_KEY=..."
    )
