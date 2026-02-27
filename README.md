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

---

## 면접봇 (Interview Bot)

개발자 기술 면접을 시뮬레이션하는 AI 면접봇입니다.
직군 → 주요 프레임워크 → 추가 기술(선택) → 경력을 선택하면 5개의 기술 질문 후 종합 평가를 반환합니다.

**지원 직군:** 프론트엔드, 백엔드, 풀스택, 데이터 분석, 데이터 엔지니어, ML/AI 엔지니어, DevOps, 클라우드 엔지니어, 모바일

### API 키 설정

세 가지 LLM 중 **하나만** 설정하면 자동으로 감지됩니다.

```bash
cp .env.example .env
```

`.env` 파일을 열어 보유한 키 하나를 입력하세요:

| 프로바이더 | 환경 변수 | 키 발급 |
|-----------|----------|--------|
| Google Gemini (무료) | `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) |
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) |
| Anthropic Claude | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |

### 실행 방법

**1. 서버 실행**
```bash
uv sync
uv run uvicorn main:app --reload
```

**2. CLI 면접 시작 (다른 터미널)**
```bash
uv run python interview_cli.py
```

방향키로 선택, 스페이스로 복수 선택(추가 기술), 엔터로 확인합니다.

### API 직접 사용 (Swagger UI)

`http://127.0.0.1:8000/docs` 에서 전체 엔드포인트를 테스트할 수 있습니다.

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /interview/options` | 직군·프레임워크·추가기술·경력 선택지 조회 |
| `POST /interview/setup` | `role`, `framework`, `extras[]`, `level` → 세션 생성 + 첫 질문 |
| `POST /interview/answer` | `session_id`, `answer` → 다음 질문 (5번째 후 종합 평가) |
| `GET /interview/result/{session_id}` | 종합 평가 재조회 |

---

## 수동 설치(uv 미사용)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn
uvicorn main:app --reload
```
