from dataclasses import dataclass, field

from pydantic import BaseModel


class InterviewResult(BaseModel):
    overall_score: int
    summary: str
    strengths: list[str]
    improvements: list[str]
    recommendation: str


@dataclass
class InterviewSession:
    session_id: str
    role: str
    framework: str
    extras: list[str]
    level: str
    system_prompt: str
    history: list[dict] = field(default_factory=list)
    question_count: int = 0
    result: dict | None = None

    @property
    def is_finished(self) -> bool:
        return self.result is not None

    @property
    def last_message(self) -> str:
        return self.history[-1]["content"] if self.history else ""
