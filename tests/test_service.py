import pytest
from unittest.mock import AsyncMock

from features.interview.domain.exceptions import (
    InvalidInputError,
    LLMQuotaExceededError,
    LLMResponseError,
    SessionNotFoundError,
)
from features.interview.domain.service import InterviewService
from features.interview.infrastructure.memory_repository import InMemorySessionRepository

VALID_SETUP = {"role": "백엔드", "framework": "FastAPI", "extras": [], "level": "신입"}
FIRST_QUESTION = "FastAPI의 비동기 처리 방식에 대해 설명해주세요."


def _make_llm(response: str = FIRST_QUESTION) -> AsyncMock:
    llm = AsyncMock()
    llm.chat.return_value = response
    return llm


def _make_service(llm=None) -> InterviewService:
    return InterviewService(
        llm=llm or _make_llm(),
        repo=InMemorySessionRepository(cleanup_interval=0),
    )


@pytest.mark.asyncio
async def test_start_creates_session():
    service = _make_service()
    session = await service.start(**VALID_SETUP)
    assert session.session_id
    assert session.question_count == 1
    assert session.last_message == FIRST_QUESTION


@pytest.mark.asyncio
async def test_start_invalid_role_raises():
    service = _make_service()
    with pytest.raises(InvalidInputError, match="유효하지 않은 직군"):
        await service.start("없는직군", "FastAPI", [], "신입")


@pytest.mark.asyncio
async def test_start_invalid_framework_raises():
    service = _make_service()
    with pytest.raises(InvalidInputError, match="유효하지 않은 프레임워크"):
        await service.start("백엔드", "없는프레임워크", [], "신입")


@pytest.mark.asyncio
async def test_answer_increments_question_count():
    llm = _make_llm()
    service = _make_service(llm)
    session = await service.start(**VALID_SETUP)
    assert session.question_count == 1

    llm.chat.return_value = "다음 질문입니다."
    session = await service.answer(session.session_id, "답변입니다.")
    assert session.question_count == 2
    assert not session.is_finished


@pytest.mark.asyncio
async def test_answer_empty_string_raises():
    service = _make_service()
    session = await service.start(**VALID_SETUP)
    with pytest.raises(InvalidInputError, match="답변을 입력해주세요"):
        await service.answer(session.session_id, "   ")


@pytest.mark.asyncio
async def test_answer_unknown_session_raises():
    service = _make_service()
    with pytest.raises(SessionNotFoundError):
        await service.answer("unknown-id", "답변")


@pytest.mark.asyncio
async def test_answer_last_question_finishes_session():
    valid_result = '{"overall_score": 8, "summary": "우수", "strengths": ["논리적"], "improvements": ["심화"], "recommendation": "합격"}'
    llm = _make_llm()
    service = _make_service(llm)
    session = await service.start(**VALID_SETUP)

    # 답변 4번 → question_count: 1→2→3→4→5 (Q5까지 전송)
    llm.chat.return_value = "다음 질문"
    for _ in range(4):
        session = await service.answer(session.session_id, "답변")

    # 5번째 답변(A5) → count=5 >= MAX_QUESTIONS → 종합 평가
    llm.chat.return_value = valid_result
    session = await service.answer(session.session_id, "마지막 답변")
    assert session.is_finished
    assert session.result["overall_score"] == 8
    assert session.result["recommendation"] == "합격"


@pytest.mark.asyncio
async def test_answer_invalid_llm_json_raises():
    llm = _make_llm()
    service = _make_service(llm)
    session = await service.start(**VALID_SETUP)

    llm.chat.return_value = "다음 질문"
    for _ in range(4):
        session = await service.answer(session.session_id, "답변")

    llm.chat.return_value = "not valid json {"
    with pytest.raises(LLMResponseError):
        await service.answer(session.session_id, "마지막 답변")


@pytest.mark.asyncio
async def test_get_result_not_finished_raises():
    service = _make_service()
    session = await service.start(**VALID_SETUP)
    with pytest.raises(InvalidInputError, match="완료되지 않았습니다"):
        service.get_result(session.session_id)


@pytest.mark.asyncio
async def test_start_invalid_level_raises():
    service = _make_service()
    with pytest.raises(InvalidInputError, match="유효하지 않은 경력"):
        await service.start("백엔드", "FastAPI", [], "99년차")


@pytest.mark.asyncio
async def test_start_invalid_extras_raises():
    service = _make_service()
    with pytest.raises(InvalidInputError, match="유효하지 않은 추가 기술"):
        await service.start("백엔드", "FastAPI", ["없는기술"], "신입")


@pytest.mark.asyncio
async def test_answer_missing_llm_fields_raises():
    """LLM이 필수 필드를 누락한 JSON을 반환하면 LLMResponseError 발생"""
    incomplete_result = '{"overall_score": 8}'  # summary, strengths 등 누락
    llm = _make_llm()
    service = _make_service(llm)
    session = await service.start(**VALID_SETUP)

    llm.chat.return_value = "다음 질문"
    for _ in range(4):
        session = await service.answer(session.session_id, "답변")

    llm.chat.return_value = incomplete_result
    with pytest.raises(LLMResponseError):
        await service.answer(session.session_id, "마지막 답변")


@pytest.mark.asyncio
async def test_start_quota_error_raises_quota_exception():
    llm = _make_llm()
    llm.chat.side_effect = RuntimeError("429 RESOURCE_EXHAUSTED. Please retry in 12.3s.")
    service = _make_service(llm)
    with pytest.raises(LLMQuotaExceededError, match="12초"):
        await service.start(**VALID_SETUP)


@pytest.mark.asyncio
async def test_session_deleted_after_finish():
    """면접 종료 후 세션이 즉시 삭제되는지 확인"""
    valid_result = '{"overall_score": 7, "summary": "보통", "strengths": ["성실"], "improvements": ["심화"], "recommendation": "보류"}'
    llm = _make_llm()
    repo = InMemorySessionRepository(cleanup_interval=0)
    service = InterviewService(llm=llm, repo=repo)
    session = await service.start(**VALID_SETUP)
    sid = session.session_id

    llm.chat.return_value = "다음 질문"
    for _ in range(4):
        session = await service.answer(sid, "답변")

    llm.chat.return_value = valid_result
    await service.answer(sid, "마지막 답변")

    assert repo.find(sid) is None  # 세션 즉시 삭제 확인
