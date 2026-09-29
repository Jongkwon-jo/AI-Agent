# AI-Agent — 파이썬으로 처음 만들어보는 AI 에이전트

초보자 눈높이에 맞춰 **Claude API** 로 AI 에이전트를 한 단계씩 만들어보는 프로젝트입니다.

## AI 에이전트란?

> **에이전트 = LLM(두뇌) + 도구(손발) + 반복(loop)**

일반 챗봇은 질문에 "말로만" 답합니다.
에이전트는 필요하면 **도구를 직접 사용**(계산하기, 파일 저장하기, 시간 확인하기 등)하고,
그 결과를 보고 다음 행동을 스스로 결정하며 일을 끝까지 해냅니다.

```
사용자 요청 → Claude: "계산기 도구 써야겠다" → 우리 코드가 계산기 실행
           → 결과를 Claude 에게 전달 → Claude: "이제 답할 수 있다" → 최종 답변
```

## 준비하기

### 1. 파이썬 설치 확인 (3.10 이상)
```bash
python --version
```

### 2. 가상환경 만들기 (권장)
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

### 3. 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
1. https://platform.claude.com/settings/keys 에서 API 키를 발급받습니다.
2. `.env.example` 파일을 복사해서 `.env` 를 만들고, 키를 붙여넣습니다.
   ```bash
   cp .env.example .env
   ```
> ⚠️ `.env` 파일은 `.gitignore` 에 등록되어 있어 GitHub 에 올라가지 않습니다. API 키는 절대 공유하지 마세요.

## 단계별 학습

| 단계 | 파일 | 배우는 내용 |
|---|---|---|
| 1 | `step1_hello.py` | Claude 에게 질문 한 번 보내고 답 받기 |
| 2 | `step2_chat.py` | 대화 기록(`messages`)을 쌓아서 이전 대화를 기억하게 하기 |
| 3 | `step3_agent.py` + `tools.py` | 도구를 정의하고, **에이전트 루프**로 도구를 스스로 쓰게 하기 |

```bash
python step1_hello.py
python step2_chat.py
python step3_agent.py
```

### 3단계에서 시도해볼 질문
- `지금 몇 시야?` → `get_current_time` 도구 사용
- `12345 * 6789 + 100 은?` → `calculator` 도구 사용
- `내일 오후 3시에 팀 회의라고 메모해줘` → `save_note` 도구 사용
- `내 메모 보여줘` → `read_notes` 도구 사용

화면에 `[도구 실행]`, `[도구 결과]` 가 찍히는 것을 보면 에이전트가 어떻게 생각하고 움직이는지 알 수 있습니다.

## 우리 서버의 vLLM 모델로 실행하기 (`local_llm/` 폴더)

Claude API 대신 연구원 서버에 올라간 **vLLM** 모델로도 똑같은 실습을 할 수 있습니다.
vLLM 은 OpenAI 와 같은 형식의 API 를 제공하므로 `openai` 라이브러리를 사용합니다.

### 1. SSH 터널 열기 (터미널을 하나 따로 열어서 실행)
```bash
ssh -N -p 10521 -L 8100:127.0.0.1:8000 work@max.gntp.or.kr
```
- 비밀번호를 입력하고 나면 **아무것도 출력되지 않은 채 멈춰 있는 것이 정상**입니다. 이 창은 닫지 말고 그대로 두세요.
- 의미: 내 컴퓨터의 `8100` 포트 → 서버 안의 `127.0.0.1:8000` (vLLM) 으로 연결됩니다.
- Windows 에서는 PowerShell 에서 같은 명령어를 쓰면 됩니다.

### 2. 다른 터미널에서 실행
```bash
python local_llm/step0_check.py   # 연결 확인 + 서버에 있는 모델 이름 출력
python local_llm/step1_hello.py   # 질문 한 번
python local_llm/step2_chat.py    # 대화 기억
python local_llm/step3_agent.py   # 도구를 쓰는 에이전트
```
설정은 `.env` 의 `VLLM_BASE_URL`, `VLLM_API_KEY`, `VLLM_MODEL` 로 바꿀 수 있습니다. (`.env.example` 참고)

### 3. 도구 호출 켜기 (3단계용)
3단계 에이전트는 모델이 도구를 호출할 수 있어야 합니다. vLLM 을 실행할 때 아래 옵션이 필요합니다.
```bash
vllm serve <모델이름> --enable-auto-tool-choice --tool-call-parser <파서>
```
| 모델 계열 | `--tool-call-parser` |
|---|---|
| Qwen2.5 / Qwen3 | `hermes` |
| Llama 3.1 / 3.2 / 3.3 | `llama3_json` |
| Mistral | `mistral` |

옵션 없이 실행된 서버라면 `step3_agent.py` 실행 시 "서버가 요청을 거절했습니다" 메시지가 나옵니다. 서버 관리자에게 옵션 추가를 요청하세요.

## 파일 구조

```
AI-Agent/
├── config.py         # 모델 이름 등 공통 설정
├── tools.py          # 에이전트가 쓰는 도구들 (함수 + 설명서)
├── step1_hello.py    # 1단계: 질문 한 번
├── step2_chat.py     # 2단계: 대화 기억
├── step3_agent.py    # 3단계: 도구를 쓰는 에이전트
├── local_llm/        # vLLM(우리 서버) 버전: step0~3
├── requirements.txt  # 필요한 라이브러리 목록
└── .env.example      # API 키 설정 예시
```

## 직접 도구 추가해보기 (연습 문제)

`tools.py` 에 새 도구를 추가하려면 세 곳만 수정하면 됩니다.
1. 일을 하는 **함수** 작성 (예: `def roll_dice() -> str:`)
2. `TOOLS` 리스트에 **설명서** 추가 (이름, 설명, 입력 형식)
3. `TOOL_FUNCTIONS` 에 `"이름": 함수` 연결

아이디어: 주사위 굴리기, 단위 변환기, 할 일 목록(추가/완료/조회), 텍스트 파일 읽기 등

## 참고

- 모델: `claude-opus-5-5` (`config.py` 에서 변경 가능)
- `config.py` 의 `FALLBACK_OPTIONS` 는 안전 필터가 요청을 거절했을 때 서버가 자동으로 다른 모델로 재시도하게 하는 옵션입니다. 필요 없으면 빼도 됩니다.
- 공식 문서: https://platform.claude.com/docs
