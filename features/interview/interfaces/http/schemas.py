from pydantic import BaseModel

from features.interview.domain.model import InterviewResult


class RoleOptions(BaseModel):
    frameworks: list[str]
    extras: list[str]


class OptionsResponse(BaseModel):
    roles: dict[str, RoleOptions]
    levels: list[str]


class SetupResponse(BaseModel):
    session_id: str
    question_number: int
    question: str


class AnswerResponse(BaseModel):
    session_id: str
    finished: bool
    question_number: int | None = None
    question: str | None = None
    result: InterviewResult | None = None


class SessionSetup(BaseModel):
    role: str
    framework: str
    extras: list[str]
    level: str


class ResultResponse(BaseModel):
    session_id: str
    setup: SessionSetup
    result: InterviewResult
