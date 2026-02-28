import threading
import time

from features.interview.domain.model import InterviewSession
from features.interview.domain.repository import ISessionRepository

_DEFAULT_TTL = 60 * 60       # 1시간
_DEFAULT_CLEANUP = 10 * 60   # 10분


class InMemorySessionRepository(ISessionRepository):
    def __init__(self, ttl_seconds: int = _DEFAULT_TTL, cleanup_interval: int = _DEFAULT_CLEANUP):
        self._store: dict[str, InterviewSession] = {}
        self._timestamps: dict[str, float] = {}
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
        if cleanup_interval > 0:
            self._start_cleanup_worker(cleanup_interval)

    def save(self, session: InterviewSession) -> None:
        with self._lock:
            self._store[session.session_id] = session
            self._timestamps[session.session_id] = time.monotonic()

    def find(self, session_id: str) -> InterviewSession | None:
        with self._lock:
            if session_id not in self._store:
                return None
            if self._is_expired(session_id):
                self._remove(session_id)
                return None
            return self._store[session_id]

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._remove(session_id)

    def _remove(self, session_id: str) -> None:
        self._store.pop(session_id, None)
        self._timestamps.pop(session_id, None)

    def _is_expired(self, session_id: str) -> bool:
        ts = self._timestamps.get(session_id)
        if ts is None:
            return True
        return time.monotonic() - ts > self._ttl

    def _cleanup(self) -> None:
        with self._lock:
            expired = [sid for sid in list(self._store) if self._is_expired(sid)]
            for sid in expired:
                self._remove(sid)

    def _start_cleanup_worker(self, interval: int) -> None:
        def worker():
            while True:
                time.sleep(interval)
                self._cleanup()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
