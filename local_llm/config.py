"""
vLLM 서버에 접속하기 위한 설정 파일입니다.

vLLM 은 OpenAI 와 같은 형식의 API 를 제공하기 때문에,
openai 라이브러리의 주소(base_url)만 우리 서버로 바꾸면 그대로 쓸 수 있습니다.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# SSH 터널을 열어두면 내 컴퓨터의 8100 포트가 서버의 vLLM(8000 포트)으로 연결됩니다.
BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8100/v1")

# vLLM 을 --api-key 옵션 없이 실행했다면 아무 값이나 넣어도 됩니다.
API_KEY = os.getenv("VLLM_API_KEY", "EMPTY")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


def get_model_name() -> str:
    """사용할 모델 이름. .env 에 VLLM_MODEL 이 없으면 서버에 올라간 첫 번째 모델을 씁니다."""
    name = os.getenv("VLLM_MODEL")
    if name:
        return name
    return client.models.list().data[0].id


MODEL = get_model_name()
MAX_TOKENS = 2048
