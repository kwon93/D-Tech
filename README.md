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
