from __future__ import annotations

from dataclasses import dataclass

from features.interview.domain.llm_port import LLMPort


@dataclass(frozen=True)
class _ProviderEntry:
    name: str
    provider: LLMPort


class FailoverLLMProvider(LLMPort):
    def __init__(self, providers: list[tuple[str, LLMPort]]):
        if not providers:
            raise ValueError("폴백할 LLM provider가 없습니다.")
        self._providers = [_ProviderEntry(name=n, provider=p) for n, p in providers]

    async def chat(self, system_prompt: str, history: list[dict], json_mode: bool = False) -> str:
        errors: list[str] = []
        last_error: Exception | None = None

        for idx, entry in enumerate(self._providers):
            try:
                return await entry.provider.chat(system_prompt, history, json_mode=json_mode)
            except Exception as e:
                last_error = e
                errors.append(f"{entry.name}: {e}")
                has_next = idx < len(self._providers) - 1
                if has_next and _is_quota_or_rate_limit_error(e):
                    continue
                raise RuntimeError(" | ".join(errors)) from e

        raise RuntimeError(" | ".join(errors)) from last_error


def _is_quota_or_rate_limit_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    markers = (
        "resource_exhausted",
        "quota exceeded",
        "rate limit",
        "rate-limit",
        "too many requests",
        "http 429",
        "status code: 429",
        "error code: 429",
    )
    return any(marker in msg for marker in markers)
