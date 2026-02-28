import sys

import questionary
import requests

BASE_URL = "http://127.0.0.1:8000"


def _extract_error_detail(resp: requests.Response) -> str:
    content_type = (resp.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        try:
            data = resp.json()
            if isinstance(data, dict):
                return str(data.get("detail") or data.get("message") or data)
            return str(data)
        except ValueError:
            pass
    text = (resp.text or "").strip()
    return text if text else f"HTTP {resp.status_code}"


def _parse_json_or_exit(resp: requests.Response, fallback_message: str) -> dict:
    try:
        data = resp.json()
    except ValueError:
        print(f"{fallback_message}: 서버가 JSON이 아닌 응답을 반환했습니다.")
        sys.exit(1)
    if not isinstance(data, dict):
        print(f"{fallback_message}: 응답 형식이 올바르지 않습니다.")
        sys.exit(1)
    return data


def _post(path: str, payload: dict) -> dict:
    try:
        resp = requests.post(f"{BASE_URL}{path}", json=payload, timeout=30)
        resp.raise_for_status()
        return _parse_json_or_exit(resp, "요청 처리에 실패했습니다")
    except requests.exceptions.ConnectionError:
        print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("요청 시간이 초과되었습니다. 잠시 후 다시 시도하세요.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        detail = _extract_error_detail(e.response) if e.response is not None else str(e)
        print(f"오류: {detail}")
        sys.exit(1)


def main():
    # 선택지 조회
    try:
        resp = requests.get(f"{BASE_URL}/interview/options", timeout=30)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("요청 시간이 초과되었습니다. 잠시 후 다시 시도하세요.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        detail = _extract_error_detail(e.response) if e.response is not None else str(e)
        print(f"선택지를 불러오지 못했습니다: {detail}")
        sys.exit(1)

    options = _parse_json_or_exit(resp, "선택지 조회에 실패했습니다")
    roles: dict = options["roles"]
    levels: list = options["levels"]

    print("\n========== 개발자 기술 면접봇 ==========\n")

    # 직군 선택
    role = questionary.select("직군을 선택하세요:", choices=list(roles.keys())).ask()
    if role is None:
        sys.exit(0)

    # 주요 프레임워크 선택 (단일)
    framework = questionary.select(
        "주요 프레임워크를 선택하세요:",
        choices=roles[role]["frameworks"],
    ).ask()
    if framework is None:
        sys.exit(0)

    # 추가 기술 선택 (복수, 선택사항)
    extras = questionary.checkbox(
        "추가 기술을 선택하세요 (선택사항, 스페이스로 선택 / 엔터로 건너뛰기):",
        choices=roles[role]["extras"],
    ).ask()
    if extras is None:
        sys.exit(0)

    # 경력 선택
    level = questionary.select("경력을 선택하세요:", choices=levels).ask()
    if level is None:
        sys.exit(0)

    stacks_desc = framework if not extras else f"{framework} + {' + '.join(extras)}"
    print(f"\n[ {role} / {stacks_desc} / {level} ] 면접을 시작합니다...\n")

    # 세션 생성
    data = _post("/interview/setup", {"role": role, "framework": framework, "extras": extras, "level": level})
    session_id = data["session_id"]

    print(f"[질문 {data['question_number']}/5]")
    print(data["question"])

    # 답변 루프
    while True:
        print()
        answer = questionary.text("답변:").ask()
        if answer is None:
            sys.exit(0)
        if not answer.strip():
            print("답변을 입력해주세요.")
            continue

        data = _post("/interview/answer", {"session_id": session_id, "answer": answer})

        if data["finished"]:
            result = data["result"]
            print("\n========== 종합 평가 ==========")
            print(f"종합 점수: {result['overall_score']} / 10")
            print(f"평가 요약: {result['summary']}")
            print(f"강점: {', '.join(result['strengths'])}")
            print(f"개선점: {', '.join(result['improvements'])}")
            print(f"결과: {result['recommendation']}")
            print("================================\n")
            break

        print(f"\n[질문 {data['question_number']}/5]")
        print(data["question"])


if __name__ == "__main__":
    main()
