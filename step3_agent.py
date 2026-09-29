"""
[3단계] 도구를 쓰는 AI 에이전트

에이전트 = LLM + 도구 + 반복(loop)

  1. 사용자의 요청을 Claude 에게 보낸다.
  2. Claude 가 "이 도구를 이 값으로 실행해줘" 라고 답하면 (stop_reason == "tool_use")
  3. 우리가 그 도구를 실행하고, 결과를 다시 Claude 에게 보낸다.
  4. Claude 가 더 이상 도구가 필요 없다고 할 때까지 2~3 을 반복한다.

실행:  python step3_agent.py   (종료하려면 'quit' 입력)
"""

import anthropic

from config import FALLBACK_OPTIONS, MAX_TOKENS, MODEL
from tools import TOOLS, run_tool

client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "너는 사용자를 돕는 한국어 AI 비서야. "
    "필요하면 주어진 도구를 사용하고, 계산은 반드시 calculator 도구로 해."
)

# 무한 반복을 막기 위한 안전장치: 한 번의 요청에서 도구를 최대 몇 번까지 쓸지
MAX_STEPS = 10


def run_agent(messages: list) -> str:
    """에이전트 루프: Claude 가 일을 끝낼 때까지 도구 실행을 반복합니다."""
    for step in range(MAX_STEPS):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            **FALLBACK_OPTIONS,
        )

        # Claude 의 답변은 항상 대화 기록에 추가합니다.
        messages.append({"role": "assistant", "content": response.content})

        # (A) 도구를 쓰고 싶다는 요청이 아니면 → 끝!
        if response.stop_reason != "tool_use":
            if response.stop_reason == "refusal":
                return "(Claude 가 이 요청에는 답하지 않았습니다.)"
            if response.stop_reason == "max_tokens":
                print("  [알림] 답변이 너무 길어서 중간에 잘렸습니다.")
            return "".join(b.text for b in response.content if b.type == "text")

        # (B) 도구 요청이면 → 요청된 도구를 모두 실행하고 결과를 모읍니다.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"  [도구 실행] {block.name}({block.input})")
            try:
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,  # 어떤 요청에 대한 결과인지 표시
                    "content": result,
                })
            except Exception as error:
                # 도구가 실패해도 멈추지 않고, 에러 내용을 Claude 에게 알려줍니다.
                result = f"에러: {error}"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": True,
                })
            print(f"  [도구 결과] {result}")

        # 도구 결과들을 '한 번에' user 메시지로 보내고, 다시 반복합니다.
        messages.append({"role": "user", "content": tool_results})

    return "(도구를 너무 많이 사용해서 중단했습니다.)"


def main():
    messages = []
    print("AI 에이전트를 시작합니다. 끝내려면 'quit' 을 입력하세요.")
    print("예) '지금 몇 시야?', '12345 * 6789 는?', '내일 3시 회의라고 메모해줘'\n")

    while True:
        user_input = input("나: ").strip()
        if user_input.lower() in ("quit", "exit", "종료"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        answer = run_agent(messages)
        print(f"에이전트: {answer}\n")


if __name__ == "__main__":
    main()
