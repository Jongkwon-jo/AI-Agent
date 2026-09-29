"""
[2단계] 대화를 기억하는 챗봇 (vLLM)

모델은 이전 대화를 스스로 기억하지 못하므로, 대화 기록을 쌓아서 매번 통째로 보냅니다.
실행:  python local_llm/step2_chat.py   (종료하려면 'quit' 입력)
"""

from config import MAX_TOKENS, MODEL, client

messages = [
    {"role": "system", "content": "너는 친절한 한국어 대화 상대야. 짧고 명확하게 답해줘."},
]

print(f"[모델] {MODEL}")
print("대화를 시작합니다. 끝내려면 'quit' 을 입력하세요.\n")

while True:
    user_input = input("나: ").strip()
    if user_input.lower() in ("quit", "exit", "종료"):
        break
    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
    )
    answer = response.choices[0].message.content

    messages.append({"role": "assistant", "content": answer})
    print(f"AI: {answer}\n")
