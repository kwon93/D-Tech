import json
import logging
import re
import uuid

from pydantic import ValidationError as PydanticValidationError

from app.core.context import request_id_var
from app.core.constants import LEVELS, MAX_QUESTIONS, ROLES
from app.core.exceptions import (
    InvalidInputError,
    LLMQuotaExceededError,
    LLMServiceUnavailableError,
    LLMResponseError,
    SessionNotFoundError,
)
from app.core.llm.port import LLMPort
from app.models.interview import InterviewResult, InterviewSession
from app.repositories.base import ISessionRepository

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self, llm: LLMPort, repo: ISessionRepository):
        self._llm = llm
        self._repo = repo

    async def start(self, role: str, framework: str, extras: list[str], level: str) -> InterviewSession:
        self._validate_setup(role, framework, extras, level)

        session_id = str(uuid.uuid4())
        system_prompt = self._build_system_prompt(role, framework, extras, level)
        provider_name = type(self._llm).__name__

        history = [{"role": "user", "content": "면접을 시작해주세요. 첫 번째 질문을 해주세요."}]
        rid = request_id_var.get()
        logger.info("LLM 첫 번째 질문 요청", extra={"request_id": rid, "session_id": session_id, "provider": provider_name})
        try:
            first_question = await self._llm.chat(system_prompt, history)
        except Exception as e:
            raise self._map_llm_exception(e, "LLM 첫 질문 생성") from e
        history.append({"role": "assistant", "content": first_question})

        session = InterviewSession(
            session_id=session_id,
            role=role,
            framework=framework,
            extras=extras,
            level=level,
            system_prompt=system_prompt,
            history=history,
            question_count=1,
        )
        self._repo.save(session)
        logger.info("세션 생성 완료", extra={"request_id": rid, "session_id": session_id, "role": role, "level": level})
        return session

    async def answer(self, session_id: str, answer: str) -> InterviewSession:
        session = self._repo.find(session_id)
        if not session:
            raise SessionNotFoundError("세션을 찾을 수 없습니다.")

        answer = answer.strip()
        if not answer:
            raise InvalidInputError("답변을 입력해주세요.")

        provider_name = type(self._llm).__name__
        session.history.append({"role": "user", "content": answer})

        rid = request_id_var.get()
        if session.question_count >= MAX_QUESTIONS:
            logger.info("LLM 종합 평가 요청", extra={"request_id": rid, "session_id": session_id, "provider": provider_name})
            try:
                result_text = await self._llm.chat(session.system_prompt, session.history, json_mode=True)
            except Exception as e:
                raise self._map_llm_exception(e, "LLM 종합 평가 생성") from e
            try:
                result_data = json.loads(result_text)
                validated = InterviewResult(**result_data)
                session.result = validated.model_dump()
            except (json.JSONDecodeError, PydanticValidationError) as e:
                raise LLMResponseError(f"LLM 응답 파싱/검증 실패: {e}") from e
            session.history.append({"role": "assistant", "content": result_text})
            self._repo.delete(session_id)
            logger.info("면접 종료 및 세션 삭제", extra={"request_id": rid, "session_id": session_id, "score": session.result.get("overall_score")})
            return session
        else:
            next_q_num = session.question_count + 1
            logger.info("LLM 다음 질문 요청", extra={"request_id": rid, "session_id": session_id, "q": next_q_num, "provider": provider_name})
            try:
                next_question = await self._llm.chat(session.system_prompt, session.history)
            except Exception as e:
                raise self._map_llm_exception(e, "LLM 다음 질문 생성") from e
            session.history.append({"role": "assistant", "content": next_question})
            session.question_count = next_q_num

        self._repo.save(session)
        return session

    @staticmethod
    def _map_llm_exception(exc: Exception, phase: str) -> LLMResponseError:
        message = str(exc)
        lowered = message.lower()
        quota_markers = ("resource_exhausted", "quota exceeded", "rate limit", "too many requests")
        unavailable_markers = (
            "service unavailable",
            "status': 'unavailable'",
            "status: unavailable",
            "high demand",
            "http 503",
            "status code: 503",
            "error code: 503",
            " 503 ",
        )
        if any(marker in lowered for marker in quota_markers):
            retry_after = _extract_retry_after_seconds(lowered)
            return LLMQuotaExceededError(retry_after_seconds=retry_after)
        if any(marker in lowered for marker in unavailable_markers):
            return LLMServiceUnavailableError()
        return LLMResponseError(f"{phase} 실패: {message}")

    def get_result(self, session_id: str) -> InterviewSession:
        session = self._repo.find(session_id)
        if not session:
            raise SessionNotFoundError("세션을 찾을 수 없습니다.")
        if not session.is_finished:
            raise InvalidInputError("아직 면접이 완료되지 않았습니다.")
        return session

    @staticmethod
    def _validate_setup(role: str, framework: str, extras: list[str], level: str) -> None:
        if role not in ROLES:
            raise InvalidInputError(f"유효하지 않은 직군: {role}")
        role_data = ROLES[role]
        if framework not in role_data["frameworks"]:
            raise InvalidInputError(f"유효하지 않은 프레임워크: {framework}")
        if level not in LEVELS:
            raise InvalidInputError(f"유효하지 않은 경력: {level}")
        invalid_extras = [e for e in extras if e not in role_data["extras"]]
        if invalid_extras:
            raise InvalidInputError(f"유효하지 않은 추가 기술: {', '.join(invalid_extras)}")

    @staticmethod
    def _build_system_prompt(role: str, framework: str, extras: list[str], level: str) -> str:
        stacks_str = ", ".join([framework] + extras)
        if extras:
            focus_note = f"주요 프레임워크인 {framework}에 집중하되, {', '.join(extras)} 관련 질문도 포함하세요."
        else:
            focus_note = f"주요 프레임워크인 {framework}에 집중해서 질문하세요."
        return f"""당신은 {role} 개발자 기술 면접관입니다.
지원자는 {stacks_str} 기술을 사용하는 {level} 개발자입니다.

면접 규칙:
- 질문만 하세요. 답변에 대한 피드백이나 평가는 하지 마세요.
- 한 번에 하나의 질문만 하세요.
- {focus_note}
- 경력 수준({level})에 맞는 난이도로 질문하세요.
- 총 {MAX_QUESTIONS}개의 질문을 진행합니다.
- {MAX_QUESTIONS}번째 답변을 받은 후에는 아래 JSON 형식으로만 종합 평가를 반환하세요:

{{
  "overall_score": <1-10 정수>,
  "summary": "<전반적인 평가 요약>",
  "strengths": ["<강점1>", "<강점2>"],
  "improvements": ["<개선점1>", "<개선점2>"],
  "recommendation": "<합격 / 불합격 / 보류>"
}}"""


def _extract_retry_after_seconds(message: str) -> int | None:
    match = re.search(r"retry in\s+(\d+(\.\d+)?)s", message)
    if not match:
        return None
    return int(float(match.group(1)))
