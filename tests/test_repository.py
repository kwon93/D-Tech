import time

import pytest

from features.interview.domain.model import InterviewSession
from features.interview.infrastructure.memory_repository import InMemorySessionRepository


def _make_session(session_id: str = "test-id") -> InterviewSession:
    return InterviewSession(
        session_id=session_id,
        role="백엔드",
        framework="FastAPI",
        extras=[],
        level="신입",
        system_prompt="test",
        history=[],
        question_count=1,
    )


def test_save_and_find():
    repo = InMemorySessionRepository(cleanup_interval=0)
    session = _make_session()
    repo.save(session)
    found = repo.find(session.session_id)
    assert found is not None
    assert found.session_id == session.session_id


def test_find_nonexistent_returns_none():
    repo = InMemorySessionRepository(cleanup_interval=0)
    assert repo.find("nonexistent") is None


def test_delete():
    repo = InMemorySessionRepository(cleanup_interval=0)
    session = _make_session()
    repo.save(session)
    repo.delete(session.session_id)
    assert repo.find(session.session_id) is None


def test_save_overwrites():
    repo = InMemorySessionRepository(cleanup_interval=0)
    session = _make_session()
    repo.save(session)
    session.question_count = 3
    repo.save(session)
    found = repo.find(session.session_id)
    assert found is not None
    assert found.question_count == 3


def test_ttl_expiry():
    repo = InMemorySessionRepository(ttl_seconds=0, cleanup_interval=0)
    session = _make_session()
    repo.save(session)
    time.sleep(0.01)
    assert repo.find(session.session_id) is None


def test_multiple_sessions():
    repo = InMemorySessionRepository(cleanup_interval=0)
    s1 = _make_session("id-1")
    s2 = _make_session("id-2")
    repo.save(s1)
    repo.save(s2)
    assert repo.find("id-1") is not None
    assert repo.find("id-2") is not None
    repo.delete("id-1")
    assert repo.find("id-1") is None
    assert repo.find("id-2") is not None
