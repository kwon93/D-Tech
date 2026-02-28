# dtech

# 디테크 타워에서 도원결의를 한 자들이여, 모여라!

## 요구사항

- Python 3.14+
- `uv` (권장) 또는 `pip`

## 실행

```powershell
cd C:\Users\93ums\PycharmProjects\dtech
uv sync
uv run uvicorn main:app --reload
```

서버 실행 후 접속:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/hello/your-name`
- `http://127.0.0.1:8000/docs`

## 수동 설치(uv 미사용)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn
uvicorn main:app --reload
```

---

## 면접봇 (interview_cli)

AI 기반 개발자 기술 면접 시뮬레이터입니다. 직군·프레임워크·경력을 선택하면 5개의 기술 질문 후 종합 평가를 반환합니다.

**LLM API 키 설정** — `.env.example`을 복사 후 하나만 입력하면 자동 감지됩니다.

```bash
cp .env.example .env
```

| 프로바이더 | 환경 변수 |
|-----------|----------|
| Google Gemini (무료) | `GEMINI_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic Claude | `ANTHROPIC_API_KEY` |

**CLI 실행** (서버 실행 후 다른 터미널)

```bash
uv run python interview_cli.py
```

**API 엔드포인트** (`/docs` 에서 직접 테스트 가능)

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /interview/options` | 직군·프레임워크·경력 선택지 조회 |
| `POST /interview/setup` | 세션 생성 + 첫 질문 반환 |
| `POST /interview/answer` | 답변 제출 → 다음 질문 또는 종합 평가 |
