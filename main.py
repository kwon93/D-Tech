import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from context import request_id_var
from features.interview.domain.exceptions import (
    InvalidInputError,
    LLMQuotaExceededError,
    LLMResponseError,
    ProviderUnavailableError,
    SessionNotFoundError,
)
from features.interview.interfaces.http.router import interview_router
from features.janis.interfaces.http.router import janis_router
from features.mindy.interfaces.http.router import mindy_router

# ── 로깅 설정 ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

# ── 앱 ────────────────────────────────────────────────────────────────────
app = FastAPI()
app.include_router(interview_router)
app.include_router(mindy_router)
app.include_router(janis_router)


# ── 요청 로깅 미들웨어 ────────────────────────────────────────────────────
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    token = request_id_var.set(request_id)
    start = time.monotonic()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        logger.info(
            "HTTP %s %s → %d (%.1fms) [%s]",
            request.method,
            request.url.path,
            status_code,
            elapsed_ms,
            request_id,
        )
        request_id_var.reset(token)


# ── 전역 예외 핸들러 ──────────────────────────────────────────────────────
@app.exception_handler(SessionNotFoundError)
async def session_not_found_handler(request: Request, exc: SessionNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidInputError)
async def invalid_input_handler(request: Request, exc: InvalidInputError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ProviderUnavailableError)
async def provider_unavailable_handler(request: Request, exc: ProviderUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(LLMQuotaExceededError)
async def llm_quota_exceeded_handler(request: Request, exc: LLMQuotaExceededError):
    logger.warning("LLM 쿼터 초과: %s", exc)
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.exception_handler(LLMResponseError)
async def llm_response_error_handler(request: Request, exc: LLMResponseError):
    logger.error("LLM 응답 오류: %s", exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})


# ── 기본 엔드포인트 ───────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Hello Wein!"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
