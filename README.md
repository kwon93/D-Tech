# dtech

# 디테크 타워에서 도원결의를 한 자들이여, 모여라!

## 요구사항

- Python 3.14+
- `uv` (권장) 또는 `pip`

## 실행

```bash
uv sync
uv run uvicorn app.main:app --reload
```

서버 실행 후 접속:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/hello/your-name`
- `http://127.0.0.1:8000/docs`

## 수동 설치 (uv 미사용)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install fastapi uvicorn python-dotenv
uvicorn app.main:app --reload
```

---

## 프로젝트 구조

```
app/
├── main.py               # FastAPI 앱 진입점
├── config.py             # 환경변수 설정
├── dependencies.py       # 공유 의존성 주입
├── api/
│   └── v1/
│       ├── router.py     # 라우터 등록
│       └── endpoints/    # 엔드포인트
│           ├── interview.py
│           ├── janis.py
│           └── mindy.py
├── models/               # 도메인 모델
├── schemas/              # Pydantic 요청/응답 스키마
├── services/             # 비즈니스 로직
├── repositories/         # 데이터 접근 레이어
└── core/                 # 공통 유틸리티 & 인프라
    ├── exceptions.py
    ├── constants.py
    ├── context.py
    └── llm/              # LLM 프로바이더 (Gemini, OpenAI, Claude)
tests/
interview_cli.py          # 대화형 CLI 클라이언트
```

---

## 면접봇 (interview)

AI 기반 개발자 기술 면접 시뮬레이터입니다. 직군·프레임워크·경력을 선택하면 5개의 기술 질문 후 종합 평가를 반환합니다.

### LLM API 키 설정

`.env.example`을 복사 후 하나 이상 입력하면 자동 감지됩니다. 여러 키를 설정하면 쿼터 초과 시 자동으로 다음 프로바이더로 failover됩니다.

```bash
cp .env.example .env
```

| 프로바이더 | 환경 변수 |
|-----------|----------|
| Google Gemini (무료) | `GEMINI_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic Claude | `ANTHROPIC_API_KEY` |

### CLI 실행 (서버 실행 후 다른 터미널)

```bash
uv run python interview_cli.py
```

### API 엔드포인트 (`/docs` 에서 직접 테스트 가능)

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /interview/options` | 직군·프레임워크·경력 선택지 조회 |
| `POST /interview/setup` | 세션 생성 + 첫 질문 반환 |
| `POST /interview/answer` | 답변 제출 → 다음 질문 또는 종합 평가 |
| `GET /interview/result/{session_id}` | 완료된 면접 결과 조회 |

---

## 테스트

```bash
uv run pytest tests/ -v
```
