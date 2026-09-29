"""
에이전트가 사용할 '도구(tool)'들을 모아둔 파일입니다.

도구 하나를 만들려면 두 가지가 필요합니다.
  1) 실제로 일을 하는 파이썬 함수
  2) Claude 에게 보여줄 도구 설명서 (이름, 설명, 입력 형식)
"""

import ast
import operator
from datetime import datetime
from pathlib import Path

NOTES_FILE = Path(__file__).parent / "notes.txt"


# ---------------------------------------------------------------------------
# 1) 실제로 일을 하는 파이썬 함수들
# ---------------------------------------------------------------------------

def get_current_time() -> str:
    """지금 날짜와 시각을 알려줍니다."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 계산기에서 허용할 연산자 목록 (+, -, *, /, **, %)
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _evaluate(node):
    """수식을 안전하게 계산합니다. (eval() 은 위험해서 쓰지 않습니다)"""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("숫자와 + - * / ** % 괄호만 사용할 수 있습니다.")


def calculator(expression: str) -> str:
    """'(3 + 4) * 2' 같은 수식을 계산합니다."""
    result = _evaluate(ast.parse(expression, mode="eval").body)
    return str(result)


def save_note(text: str) -> str:
    """메모를 notes.txt 파일에 한 줄 추가합니다."""
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{get_current_time()}] {text}\n")
    return "메모를 저장했습니다."


def read_notes() -> str:
    """저장된 메모를 모두 읽어옵니다."""
    if not NOTES_FILE.exists():
        return "저장된 메모가 없습니다."
    return NOTES_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 2) Claude 에게 보여줄 도구 설명서
#    Claude 는 이 설명을 읽고 "언제, 어떤 도구를, 어떤 값으로" 쓸지 스스로 결정합니다.
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "get_current_time",
        "description": "현재 날짜와 시각을 알려준다. 오늘 날짜나 지금 시간이 필요할 때 사용한다.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "calculator",
        "description": "사칙연산 수식을 정확하게 계산한다. 숫자 계산이 필요하면 항상 이 도구를 사용한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "계산할 수식. 예: '(3 + 4) * 2'",
                },
            },
            "required": ["expression"],
        },
    },
    {
        "name": "save_note",
        "description": "사용자가 기억해달라고 한 내용을 메모 파일에 저장한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "저장할 메모 내용"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "read_notes",
        "description": "지금까지 저장된 메모를 모두 읽어온다.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

# 도구 이름 → 실제 함수 연결표
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "calculator": calculator,
    "save_note": save_note,
    "read_notes": read_notes,
}


def run_tool(name: str, tool_input: dict) -> str:
    """Claude 가 요청한 도구를 찾아서 실행하고, 결과를 문자열로 돌려줍니다."""
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        raise ValueError(f"'{name}' 이라는 도구는 없습니다.")
    return function(**tool_input)
