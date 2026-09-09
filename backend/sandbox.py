"""Sandboxed execution of AI-generated Python code.

Defenses:
  1. Static blocklist — rejects code containing dangerous tokens before execution.
  2. Restricted builtins — only safe, data-oriented builtins are exposed.
  3. Timeout — kills execution that exceeds a time limit.
"""

import ast
import threading
from typing import Any

BLOCKED_TOKENS = [
    "import os",
    "import sys",
    "import subprocess",
    "import shutil",
    "import socket",
    "import http",
    "import requests",
    "import urllib",
    "__import__",
    "importlib",
    "os.system",
    "os.popen",
    "os.exec",
    "os.remove",
    "os.unlink",
    "os.rmdir",
    "subprocess.",
    "eval(",
    "exec(",
    "compile(",
    "globals(",
    "locals(",
    "breakpoint(",
    "exit(",
    "quit(",
    "open(",
    "__builtins__",
    "__subclasses__",
    "__class__",
    "getattr(",
    "setattr(",
    "delattr(",
]

SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "frozenset": frozenset,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "print": print,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
    "True": True,
    "False": False,
    "None": None,
}

ALLOWED_MODULES = {"pandas", "numpy", "math", "datetime", "collections", "re"}

EXEC_TIMEOUT_SECONDS = 30

_real_import = __import__


def _restricted_import(name, *args, **kwargs):
    top_level = name.split(".")[0]
    if top_level not in ALLOWED_MODULES:
        raise ImportError(f"Import not allowed: {name}")
    return _real_import(name, *args, **kwargs)


class SandboxViolation(Exception):
    """Raised when AI-generated code attempts a blocked operation."""


class SandboxTimeout(Exception):
    """Raised when AI-generated code exceeds the time limit."""


def validate_code(code: str) -> None:
    for token in BLOCKED_TOKENS:
        if token in code:
            raise SandboxViolation(f"Blocked pattern detected: {token}")

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = ""
            if isinstance(node, ast.Import):
                module = node.names[0].name
            elif node.module:
                module = node.module
            top_level = module.split(".")[0]
            if top_level not in ALLOWED_MODULES:
                raise SandboxViolation(f"Import not allowed: {module}")


def safe_exec(
    code: str,
    local_scope: dict[str, Any],
    timeout: int = EXEC_TIMEOUT_SECONDS,
) -> None:
    validate_code(code)

    restricted_globals = {
        "__builtins__": {**SAFE_BUILTINS, "__import__": _restricted_import},
    }

    exception_holder: list[Exception] = []

    def _target():
        try:
            exec(code, restricted_globals, local_scope) 
        except Exception as e:
            exception_holder.append(e)

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        raise SandboxTimeout(
            f"Code execution exceeded {timeout}s time limit"
        )

    if exception_holder:
        raise exception_holder[0]
