"""
[2단계] 대화를 기억하는 챗봇

Claude 는 이전 대화를 스스로 기억하지 못합니다.
그래서 우리가 대화 기록(messages 리스트)을 계속 쌓아서 매번 통째로 보내줘야 합니다.
실행:  python step2_chat.py   (종료하려면 'quit' 입력)
"""

import anthropic

from config import FALLBACK_OPTIONS, MAX_TOKENS, MODEL

client = anthropic.Anthropic()

# 대화 기록을 담을 리스트
messages = []

print("Claude 와 대화를 시작합니다. 끝내려면 'quit' 을 입력하세요.\n")

while True:
    user_input = input("나: ").strip()
    if user_input.lower() in ("quit", "exit", "종료"):
        break
    if not user_input:
        continue

    # 1) 내 말을 기록에 추가
    messages.append({"role": "user", "content": user_input})

    # 2) 지금까지의 기록 전체를 보내기
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system="너는 친절한 한국어 대화 상대야. 짧고 명확하게 답해줘.",
        messages=messages,
        **FALLBACK_OPTIONS,
    )

    # 3) Claude 의 답도 기록에 추가 (그래야 다음 질문 때 기억합니다)
    messages.append({"role": "assistant", "content": response.content})

    answer = "".join(block.text for block in response.content if block.type == "text")
    print(f"Claude: {answer}\n")
