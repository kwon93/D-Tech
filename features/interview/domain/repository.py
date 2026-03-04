from abc import ABC, abstractmethod

from features.interview.domain.model import InterviewSession


class ISessionRepository(ABC):
    @abstractmethod
    def save(self, session: InterviewSession) -> None: ...

    @abstractmethod
    def find(self, session_id: str) -> InterviewSession | None: ...

    @abstractmethod
    def delete(self, session_id: str) -> None: ...
