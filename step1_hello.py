"""
[1단계] Claude 에게 질문 한 번 하기

가장 기본: 질문을 보내고 → 답을 받아서 → 출력합니다.
실행:  python step1_hello.py
"""

import anthropic

from config import FALLBACK_OPTIONS, MAX_TOKENS, MODEL

# 1) 클라이언트 만들기 (API 키는 환경 변수 ANTHROPIC_API_KEY 에서 자동으로 읽습니다)
client = anthropic.Anthropic()

# 2) 질문 보내기
response = client.beta.messages.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    system="너는 친절한 파이썬 선생님이야. 초보자도 이해하기 쉽게 한국어로 설명해줘.",
    messages=[
        {"role": "user", "content": "AI 에이전트가 뭔지 세 문장으로 설명해줘."},
    ],
    **FALLBACK_OPTIONS,
)

# 3) 답변 출력하기
#    response.content 는 '블록'들의 리스트입니다. 글자(text) 블록만 골라서 출력합니다.
for block in response.content:
    if block.type == "text":
        print(block.text)

# 참고: 이번 요청에 사용한 토큰 수 (요금 계산 기준)
print(f"\n[사용한 토큰] 입력: {response.usage.input_tokens}, 출력: {response.usage.output_tokens}")
