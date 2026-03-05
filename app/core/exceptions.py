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


class LLMServiceUnavailableError(LLMResponseError):
    """LLM provider 일시 장애/과부하"""

    def __init__(self):
        super().__init__("LLM 서비스가 일시적으로 혼잡합니다. 잠시 후 다시 시도해주세요.")


class ProviderUnavailableError(InterviewError):
    """LLM provider 초기화 실패/미설정"""
