"""Tests for utility functions in main.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import fix_python_syntax, strip_code_fences


class TestStripCodeFences:
    def test_removes_python_fences(self):
        raw = "```python\nprint('hello')\n```"
        result = strip_code_fences(raw)
        assert "print('hello')" in result
        assert "```" not in result

    def test_removes_plain_fences(self):
        raw = "```\nx = 1\n```"
        result = strip_code_fences(raw)
        assert "x = 1" in result
        assert "```" not in result

    def test_no_fences_unchanged(self):
        raw = "x = 1"
        assert strip_code_fences(raw) == "x = 1"

    def test_strips_surrounding_whitespace(self):
        raw = "  \n```python\nresult = 42\n```\n  "
        result = strip_code_fences(raw)
        assert "result = 42" in result
        assert "```" not in result

    def test_empty_string(self):
        assert strip_code_fences("") == ""


class TestFixPythonSyntax:
    def test_adds_colon_to_for_loop(self):
        code = "for i in range(10)\n    print(i)"
        fixed = fix_python_syntax(code)
        assert "for i in range(10):" in fixed

    def test_adds_colon_to_if_statement(self):
        code = "if x > 5\n    print(x)"
        fixed = fix_python_syntax(code)
        assert "if x > 5:" in fixed

    def test_does_not_double_colon(self):
        code = "for i in range(10):\n    print(i)"
        fixed = fix_python_syntax(code)
        assert "for i in range(10)::" not in fixed
        assert "for i in range(10):" in fixed

    def test_preserves_normal_lines(self):
        code = "x = 1\ny = 2\nresult = x + y"
        assert fix_python_syntax(code) == code

    def test_empty_string(self):
        assert fix_python_syntax("") == ""

    def test_multiline_mixed(self):

        code = "x = 10\nif x > 5\n    result = x"
        fixed = fix_python_syntax(code)
        lines = fixed.split("\n")
        assert lines[0] == "x = 10"
        assert lines[1] == "if x > 5:"
        assert lines[2] == "    result = x"
