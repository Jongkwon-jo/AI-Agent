"""모든 단계에서 함께 쓰는 설정 파일입니다."""

from dotenv import load_dotenv

# .env 파일에 적어둔 ANTHROPIC_API_KEY 를 환경 변수로 불러옵니다.
load_dotenv()

# 사용할 Claude 모델 이름
MODEL = "claude-opus-5-5"

# Claude 가 한 번에 만들 수 있는 최대 답변 길이(토큰 수)
MAX_TOKENS = 16000

# 안전 필터가 요청을 거절하면, 서버가 자동으로 다른 모델로 다시 시도하게 하는 옵션입니다.
# (client.beta.messages.create 에 **FALLBACK_OPTIONS 로 넘겨줍니다)
FALLBACK_OPTIONS = {
    "betas": ["server-side-fallback-2026-07-01"],
    "fallbacks": "default",
}
