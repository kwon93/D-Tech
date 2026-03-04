from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from features.interview.constants import LEVELS, ROLES
from features.interview.domain.enums import Level
from features.interview.domain.exceptions import ProviderUnavailableError
from features.interview.domain.service import InterviewService
from features.interview.infrastructure.memory_repository import InMemorySessionRepository
from features.interview.interfaces.http.schemas import (
    AnswerResponse,
    OptionsResponse,
    ResultResponse,
    SetupResponse,
)
from infrastructure.llm.factory import create_provider

interview_router = APIRouter(prefix="/interview", tags=["interview"])

_repo = InMemorySessionRepository()


def get_service() -> InterviewService:
    try:
        return InterviewService(create_provider(), _repo)
    except RuntimeError as e:
        raise ProviderUnavailableError(str(e)) from e


class SetupRequest(BaseModel):
    role: str
    framework: str
    extras: list[str] = Field(default_factory=list)
    level: Level  # Pydantic이 자동으로 유효한 Level 값인지 검증


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


@interview_router.get("/options", response_model=OptionsResponse)
async def get_options():
    return OptionsResponse(roles=ROLES, levels=[lv.value for lv in LEVELS])


@interview_router.post("/setup", response_model=SetupResponse)
async def setup_interview(
    req: SetupRequest,
    service: Annotated[InterviewService, Depends(get_service)],
):
    session = await service.start(req.role, req.framework, req.extras, req.level)
    return SetupResponse(
        session_id=session.session_id,
        question_number=session.question_count,
        question=session.last_message,
    )


@interview_router.post("/answer", response_model=AnswerResponse)
async def submit_answer(
    req: AnswerRequest,
    service: Annotated[InterviewService, Depends(get_service)],
):
    session = await service.answer(req.session_id, req.answer)
    if session.is_finished:
        return AnswerResponse(
            session_id=session.session_id,
            finished=True,
            result=session.result,
        )
    return AnswerResponse(
        session_id=session.session_id,
        finished=False,
        question_number=session.question_count,
        question=session.last_message,
    )


@interview_router.get("/result/{session_id}", response_model=ResultResponse)
async def get_result(
    session_id: str,
    service: Annotated[InterviewService, Depends(get_service)],
):
    session = service.get_result(session_id)
    return ResultResponse(
        session_id=session_id,
        setup={
            "role": session.role,
            "framework": session.framework,
            "extras": session.extras,
            "level": session.level,
        },
        result=session.result,
    )
