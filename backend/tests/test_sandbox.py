"""Tests for the sandboxed code execution module."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pytest

from sandbox import SandboxTimeout, SandboxViolation, safe_exec


class TestBlockedPatterns:
    def test_blocks_os_import(self):
        with pytest.raises(SandboxViolation):
            safe_exec("import os", {})

    def test_blocks_subprocess(self):
        with pytest.raises(SandboxViolation):
            safe_exec("import subprocess", {})

    def test_blocks_open(self):
        with pytest.raises(SandboxViolation):
            safe_exec("open('/etc/passwd')", {})

    def test_blocks_eval(self):
        with pytest.raises(SandboxViolation):
            safe_exec("eval('1+1')", {})

    def test_blocks_exec(self):
        with pytest.raises(SandboxViolation):
            safe_exec("exec('x=1')", {})

    def test_blocks_dunder_import(self):
        with pytest.raises(SandboxViolation):
            safe_exec("__import__('os')", {})

    def test_blocks_builtins_access(self):
        with pytest.raises(SandboxViolation):
            safe_exec("__builtins__['open']('test')", {})

    def test_blocks_getattr(self):
        with pytest.raises(SandboxViolation):
            safe_exec("getattr(__builtins__, 'open')", {})

    def test_blocks_socket(self):
        with pytest.raises(SandboxViolation):
            safe_exec("import socket", {})

    def test_blocks_shutil(self):
        with pytest.raises(SandboxViolation):
            safe_exec("import shutil", {})


class TestAllowedImports:
    def test_allows_math_via_ast(self):
        scope = {}
        safe_exec("import math\nresult = math.sqrt(16)", scope)
        assert scope["result"] == 4.0

    def test_allows_datetime(self):
        scope = {}
        safe_exec("import datetime\nresult = datetime.date(2024, 1, 1).year", scope)
        assert scope["result"] == 2024

    def test_allows_re(self):
        scope = {}
        safe_exec("import re\nresult = bool(re.match(r'\\d+', '123'))", scope)
        assert scope["result"] is True


class TestSafeExecution:
    def test_basic_arithmetic(self):
        scope = {}
        safe_exec("result = 2 + 3", scope)
        assert scope["result"] == 5

    def test_pandas_operations(self):
        df = pd.DataFrame({"Sales": [10, 20, 30]})
        scope = {"df": df, "pd": pd}
        safe_exec("result = df['Sales'].sum()", scope)
        assert scope["result"] == 60

    def test_list_comprehension(self):
        scope = {}
        safe_exec("result = [x**2 for x in range(5)]", scope)
        assert scope["result"] == [0, 1, 4, 9, 16]

    def test_string_operations(self):
        scope = {}
        safe_exec("result = 'hello world'.upper()", scope)
        assert scope["result"] == "HELLO WORLD"

    def test_safe_builtins_available(self):
        scope = {}
        safe_exec("result = len([1, 2, 3])", scope)
        assert scope["result"] == 3

    def test_sorted_available(self):
        scope = {}
        safe_exec("result = sorted([3, 1, 2])", scope)
        assert scope["result"] == [1, 2, 3]


class TestTimeout:
    def test_infinite_loop_times_out(self):
        with pytest.raises(SandboxTimeout):
            safe_exec("while True: pass", {}, timeout=1)


class TestRestrictedBuiltins:
    def test_open_not_in_builtins(self):
        with pytest.raises(SandboxViolation):
            safe_exec("f = open('test.txt')", {})

    def test_import_not_callable_from_builtins(self):
        with pytest.raises(SandboxViolation):
            safe_exec("__import__('os')", {})
