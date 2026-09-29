"""
[1단계] vLLM 모델에게 질문 한 번 하기
실행:  python local_llm/step1_hello.py
"""

from config import MAX_TOKENS, MODEL, client

print(f"[모델] {MODEL}\n")

response = client.chat.completions.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    messages=[
        # OpenAI 형식에서는 시스템 프롬프트도 messages 안에 role="system" 으로 넣습니다.
        {"role": "system", "content": "너는 친절한 파이썬 선생님이야. 초보자도 이해하기 쉽게 한국어로 설명해줘."},
        {"role": "user", "content": "AI 에이전트가 뭔지 세 문장으로 설명해줘."},
    ],
)

print(response.choices[0].message.content)
print(f"\n[사용한 토큰] 입력: {response.usage.prompt_tokens}, 출력: {response.usage.completion_tokens}")
