"""
[3단계] 도구를 쓰는 AI 에이전트 (vLLM)

Claude 버전(step3_agent.py)과 원리는 똑같습니다. API 형식만 OpenAI 방식입니다.
  1. 요청을 모델에게 보낸다.
  2. 모델이 도구 호출을 요청하면 (finish_reason == "tool_calls")
  3. 도구를 실행하고 결과를 role="tool" 메시지로 돌려준다.
  4. 모델이 더 이상 도구를 요청하지 않을 때까지 반복한다.

※ vLLM 서버가 도구 호출 옵션과 함께 실행되어 있어야 합니다. (README 참고)
실행:  python local_llm/step3_agent.py   (종료하려면 'quit' 입력)
"""

import json
import sys
from pathlib import Path

from openai import BadRequestError

from config import MAX_TOKENS, MODEL, client

# 상위 폴더의 tools.py (Claude 버전과 같은 도구)를 가져오기 위한 설정
sys.path.append(str(Path(__file__).parent.parent))
from tools import TOOLS, run_tool  # noqa: E402

# tools.py 의 도구 설명서(Claude 형식)를 OpenAI 형식으로 바꿉니다.
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        },
    }
    for tool in TOOLS
]

SYSTEM_PROMPT = (
    "너는 사용자를 돕는 한국어 AI 비서야. "
    "필요하면 주어진 도구를 사용하고, 계산은 반드시 calculator 도구로 해."
)

MAX_STEPS = 10  # 무한 반복 방지


def run_agent(messages: list) -> str:
    """에이전트 루프: 모델이 일을 끝낼 때까지 도구 실행을 반복합니다."""
    for step in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
            tools=OPENAI_TOOLS,
        )
        message = response.choices[0].message

        # 모델의 답변을 대화 기록에 추가합니다.
        messages.append(message.model_dump(exclude_none=True))

        # (A) 도구 요청이 없으면 → 끝!
        if not message.tool_calls:
            return message.content or ""

        # (B) 요청된 도구를 하나씩 실행하고, 결과를 role="tool" 로 추가합니다.
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            print(f"  [도구 실행] {name}({tool_call.function.arguments})")
            try:
                # OpenAI 형식에서는 도구 입력값이 JSON '문자열'로 옵니다.
                arguments = json.loads(tool_call.function.arguments or "{}")
                result = run_tool(name, arguments)
            except Exception as error:
                result = f"에러: {error}"
            print(f"  [도구 결과] {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,  # 어떤 요청에 대한 결과인지 표시
                "content": result,
            })

    return "(도구를 너무 많이 사용해서 중단했습니다.)"


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print(f"[모델] {MODEL}")
    print("AI 에이전트를 시작합니다. 끝내려면 'quit' 을 입력하세요.")
    print("예) '지금 몇 시야?', '12345 * 6789 는?', '내일 3시 회의라고 메모해줘'\n")

    while True:
        user_input = input("나: ").strip()
        if user_input.lower() in ("quit", "exit", "종료"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        try:
            answer = run_agent(messages)
        except BadRequestError as error:
            print(f"\n❌ 서버가 요청을 거절했습니다: {error.message}")
            print("   → vLLM 이 도구 호출 옵션 없이 실행된 것 같습니다. README 의 '도구 호출 켜기'를 참고하세요.")
            break
        print(f"에이전트: {answer}\n")


if __name__ == "__main__":
    main()
