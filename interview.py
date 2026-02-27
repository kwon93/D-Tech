import json
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm import LLMProvider, get_provider

load_dotenv()

router = APIRouter(prefix="/interview", tags=["interview"])

# 모듈 로드 시 한 번만 프로바이더 초기화
_provider: LLMProvider = get_provider()

MAX_QUESTIONS = 5

# 직군별 주요 프레임워크(단일 선택) + 추가 기술(복수 선택)
ROLES: dict[str, dict[str, list[str]]] = {
    "프론트엔드": {
        "frameworks": ["React", "Vue", "Angular", "Next.js", "Svelte"],
        "extras": ["TypeScript", "Tailwind CSS", "GraphQL", "Webpack/Vite", "Testing (Jest/RTL)"],
    },
    "백엔드": {
        "frameworks": ["Spring Boot", "FastAPI", "Django", "Node.js/Express", "NestJS", "Go/Gin", "Laravel"],
        "extras": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "GraphQL", "gRPC", "Kafka", "ElasticSearch"],
    },
    "풀스택": {
        "frameworks": ["Next.js", "Nuxt.js", "SvelteKit", "Django + React", "Rails + React"],
        "extras": ["TypeScript", "PostgreSQL", "Redis", "Docker", "GraphQL"],
    },
    "데이터 분석": {
        "frameworks": ["Python/Pandas", "SQL", "R"],
        "extras": ["Tableau", "Power BI", "Spark", "Scikit-learn", "A/B Testing"],
    },
    "데이터 엔지니어": {
        "frameworks": ["Apache Spark", "Apache Kafka", "Apache Airflow"],
        "extras": ["dbt", "Flink", "Snowflake", "BigQuery", "Databricks", "Hadoop"],
    },
    "ML/AI 엔지니어": {
        "frameworks": ["PyTorch", "TensorFlow", "Scikit-learn"],
        "extras": ["MLflow", "Hugging Face", "LangChain", "Kubernetes", "FastAPI", "CUDA"],
    },
    "DevOps": {
        "frameworks": ["Docker/Kubernetes", "GitHub Actions", "Jenkins"],
        "extras": ["AWS", "GCP", "Azure", "Terraform", "ArgoCD", "Prometheus/Grafana", "Ansible"],
    },
    "클라우드 엔지니어": {
        "frameworks": ["AWS", "GCP", "Azure"],
        "extras": ["Terraform", "Kubernetes", "Pulumi", "CDK", "Serverless", "비용 최적화"],
    },
    "모바일": {
        "frameworks": ["React Native", "Flutter", "Swift (iOS)", "Kotlin (Android)"],
        "extras": ["Firebase", "GraphQL", "REST API", "CI/CD (Fastlane)", "앱스토어 배포"],
    },
}
LEVELS = ["신입", "주니어 (1-3년)", "미들 (3-5년)", "시니어 (5년+)"]

sessions: dict = {}


class SetupRequest(BaseModel):
    role: str
    framework: str
    extras: list[str] = []
    level: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


def build_system_prompt(role: str, framework: str, extras: list[str], level: str) -> str:
    stacks = [framework] + extras
    stacks_str = ", ".join(stacks)
    extras_note = f" 추가로 {', '.join(extras)} 관련 질문도 포함하세요." if extras else ""
    return f"""당신은 {role} 개발자 기술 면접관입니다.
지원자는 {stacks_str} 기술을 사용하는 {level} 개발자입니다.

면접 규칙:
- 질문만 하세요. 답변에 대한 피드백이나 평가는 하지 마세요.
- 한 번에 하나의 질문만 하세요.
- 주요 프레임워크인 {framework}에 집중해서 질문하되,{extras_note}
- 경력 수준({level})에 맞는 난이도로 질문하세요.
- 총 {MAX_QUESTIONS}개의 질문을 진행합니다.
- {MAX_QUESTIONS}번째 답변을 받은 후에는 아래 JSON 형식으로만 종합 평가를 반환하세요:

{{
  "overall_score": <1-10 정수>,
  "summary": "<전반적인 평가 요약>",
  "strengths": ["<강점1>", "<강점2>"],
  "improvements": ["<개선점1>", "<개선점2>"],
  "recommendation": "<합격 / 불합격 / 보류>"
}}"""


@router.get("/options")
async def get_options():
    return {"roles": ROLES, "levels": LEVELS}


@router.post("/setup")
async def setup_interview(req: SetupRequest):
    if req.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 직군: {req.role}")

    role_data = ROLES[req.role]

    if req.framework not in role_data["frameworks"]:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 프레임워크: {req.framework}")

    if req.level not in LEVELS:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 경력: {req.level}")

    invalid_extras = [e for e in req.extras if e not in role_data["extras"]]
    if invalid_extras:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 추가 기술: {', '.join(invalid_extras)}")

    session_id = str(uuid.uuid4())
    system_prompt = build_system_prompt(req.role, req.framework, req.extras, req.level)

    history = [{"role": "user", "content": "면접을 시작해주세요. 첫 번째 질문을 해주세요."}]
    first_question = _provider.chat(system_prompt, history)
    history.append({"role": "assistant", "content": first_question})

    sessions[session_id] = {
        "setup": {"role": req.role, "framework": req.framework, "extras": req.extras, "level": req.level},
        "system_prompt": system_prompt,
        "history": history,
        "question_count": 1,
    }

    return {
        "session_id": session_id,
        "question_number": 1,
        "question": first_question,
    }


@router.post("/answer")
async def submit_answer(req: AnswerRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    answer = req.answer.strip()
    if not answer:
        raise HTTPException(status_code=400, detail="답변을 입력해주세요.")

    session["history"].append({"role": "user", "content": answer})

    if session["question_count"] >= MAX_QUESTIONS:
        try:
            result_text = _provider.chat(session["system_prompt"], session["history"], json_mode=True)
            result = json.loads(result_text)
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=502, detail=f"종합 평가 생성에 실패했습니다: {e}")

        session["history"].append({"role": "assistant", "content": result_text})
        session["result"] = result

        return {
            "session_id": req.session_id,
            "finished": True,
            "result": result,
        }

    next_question = _provider.chat(session["system_prompt"], session["history"])
    session["history"].append({"role": "assistant", "content": next_question})
    session["question_count"] += 1

    return {
        "session_id": req.session_id,
        "finished": False,
        "question_number": session["question_count"],
        "question": next_question,
    }


@router.get("/result/{session_id}")
async def get_result(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    if "result" not in session:
        raise HTTPException(status_code=400, detail="아직 면접이 완료되지 않았습니다.")

    return {
        "session_id": session_id,
        "setup": session["setup"],
        "result": session["result"],
    }
