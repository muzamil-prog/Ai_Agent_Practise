import ast
import json
import operator
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_FILE_CHARS = 8000

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed")
    if isinstance(node, ast.BinOp):
        op = _ALLOWED_BINOPS.get(type(node.op))
        if op is None:
            raise ValueError("Operator not allowed")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent too large")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = _ALLOWED_UNARYOPS.get(type(node.op))
        if op is None:
            raise ValueError("Operator not allowed")
        return op(_eval_node(node.operand))
    raise ValueError("Expression not allowed")


def calculator(expression: str) -> str:
    tree = ast.parse(expression, mode="eval")
    result = _eval_node(tree)
    return str(result)


def get_current_time(timezone: str = "UTC") -> str:
    try:
        zone = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown timezone: {timezone}") from exc
    now = datetime.now(zone)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


def _resolve_path(path: str) -> Path:
    target = (REPO_ROOT / path).resolve()
    if target != REPO_ROOT and REPO_ROOT not in target.parents:
        raise ValueError("Path must stay inside the repository")
    if target.name == ".env" or ".git" in target.parts:
        raise ValueError("Access to this path is blocked")
    return target


def read_text_file(path: str) -> str:
    target = _resolve_path(path)
    if not target.is_file():
        raise ValueError(f"Not a file: {path}")
    text = target.read_text(encoding="utf-8", errors="replace")
    if len(text) > MAX_FILE_CHARS:
        return text[:MAX_FILE_CHARS] + f"\n... [truncated at {MAX_FILE_CHARS} characters]"
    return text


def list_files(directory: str = ".") -> str:
    target = _resolve_path(directory)
    if not target.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    entries = sorted(
        entry.name + ("/" if entry.is_dir() else "")
        for entry in target.iterdir()
        if entry.name not in {".git", ".env"}
    )
    return "\n".join(entries) if entries else "(empty directory)"


TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "read_text_file": read_text_file,
    "list_files": list_files,
}

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression using +, -, *, /, //, %, ** and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The arithmetic expression, e.g. '(12 + 8) * 3'.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time in an IANA timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone name such as 'UTC' or 'Asia/Karachi'. Defaults to UTC.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_text_file",
            "description": "Read a UTF-8 text file inside this repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Repository-relative path, e.g. 'README.md'.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and folders inside a repository directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Repository-relative directory path. Defaults to '.'.",
                    }
                },
            },
        },
    },
]


def execute_tool(name: str, arguments_json: str) -> str:
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return f"Error: unknown tool '{name}'"
    try:
        arguments = json.loads(arguments_json or "{}")
        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a JSON object")
        return function(**arguments)
    except Exception as exc:
        return f"Error: {exc}"
