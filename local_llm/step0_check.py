"""
[0단계] vLLM 서버 연결 확인

SSH 터널을 연 상태에서 실행하세요.
실행:  python local_llm/step0_check.py
"""

import os

from dotenv import load_dotenv
from openai import APIConnectionError, OpenAI

load_dotenv()
base_url = os.getenv("VLLM_BASE_URL", "http://localhost:8100/v1")
client = OpenAI(base_url=base_url, api_key=os.getenv("VLLM_API_KEY", "EMPTY"))

print(f"접속 주소: {base_url}")
try:
    models = client.models.list().data
except APIConnectionError:
    print("❌ 서버에 연결할 수 없습니다.")
    print("   → 다른 터미널에서 SSH 터널이 열려 있는지 확인하세요. (README 참고)")
    raise SystemExit(1)

print("✅ 연결 성공! 서버에 올라간 모델:")
for model in models:
    print(f"   - {model.id}")
