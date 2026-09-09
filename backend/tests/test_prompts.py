"""Tests for LLM prompt templates."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prompts import analysis_prompt, cleaning_prompt, insight_prompt


class TestCleaningPrompt:
    def test_includes_data_audit(self):
        audit = {"columns": ["A", "B"], "dtypes": {"A": "int64", "B": "object"}}
        result = cleaning_prompt(audit)
        assert "A" in result
        assert "B" in result
        assert "int64" in result

    def test_requests_code_only(self):
        audit = {"columns": ["X"], "dtypes": {"X": "float64"}}
        result = cleaning_prompt(audit)
        assert "ONLY" in result.upper() or "code" in result.lower()


class TestAnalysisPrompt:
    def test_includes_columns(self):
        result = analysis_prompt(["Sales", "Profit"], "", "What is total sales?")
        assert "Sales" in result
        assert "Profit" in result

    def test_includes_user_question(self):
        result = analysis_prompt(["Col1"], "", "How many rows?")
        assert "How many rows?" in result

    def test_includes_chat_history(self):
        history = "user: What is total sales?\nassistant: Total sales is 500."
        result = analysis_prompt(["Sales"], history, "Follow up question")
        assert "Total sales is 500" in result

    def test_requests_result_variable(self):
        result = analysis_prompt(["X"], "", "test")
        assert "result" in result

    def test_requests_python_code(self):
        result = analysis_prompt(["X"], "", "test")
        assert "Python" in result or "code" in result.lower()


class TestInsightPrompt:
    def test_includes_question_and_result(self):
        result = insight_prompt("What is total?", 42)
        assert "What is total?" in result
        assert "42" in result

    def test_requests_business_insight(self):
        result = insight_prompt("test", 100)
        assert "insight" in result.lower()
