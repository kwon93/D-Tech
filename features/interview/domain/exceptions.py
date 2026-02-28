class InterviewError(Exception):
    """면접봇 도메인 기본 예외"""


class SessionNotFoundError(InterviewError):
    """세션을 찾을 수 없음"""


class SessionExpiredError(InterviewError):
    """세션이 만료됨"""


class InvalidInputError(InterviewError):
    """잘못된 입력값"""


class LLMResponseError(InterviewError):
    """LLM 응답 처리 실패"""


class LLMQuotaExceededError(LLMResponseError):
    """LLM 사용량 한도/요청 제한 초과"""

    def __init__(self, retry_after_seconds: int | None = None):
        self.retry_after_seconds = retry_after_seconds
        if retry_after_seconds is None:
            message = "LLM 사용량 한도를 초과했습니다. 잠시 후 다시 시도하거나 다른 API 키를 설정해주세요."
        else:
            message = f"LLM 사용량 한도를 초과했습니다. 약 {retry_after_seconds}초 후 다시 시도해주세요."
        super().__init__(message)


class ProviderUnavailableError(InterviewError):
    """LLM provider 초기화 실패/미설정"""
