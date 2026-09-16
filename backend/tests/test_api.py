"""Tests for the /analyze API endpoint."""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_ai_response(content: str):
    """Build a mock OpenAI-style chat completion."""
    choice = MagicMock()
    choice.message.content = content
    resp = MagicMock()
    resp.choices = [choice]
    return resp


class TestAnalyzeEndpoint:
    def test_csv_upload_returns_insight(self, client, sample_csv):
        cleaning_code = "pass"
        analysis_code = "result = df['Sales'].sum()"
        insight_text = "Total sales amount to 450 units."

        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response(cleaning_code),
                _mock_ai_response(analysis_code),
                _mock_ai_response(insight_text),
            ]

            resp = client.post(
                "/analyze",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "What is total sales?"},
            )

        assert resp.status_code == 200
        assert resp.json()["insight"] == insight_text

    def test_xlsx_upload_returns_insight(self, client, sample_xlsx):
        cleaning_code = "pass"
        analysis_code = "result = df['Revenue'].sum()"
        insight_text = "Total revenue is 12500."

        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response(cleaning_code),
                _mock_ai_response(analysis_code),
                _mock_ai_response(insight_text),
            ]

            resp = client.post(
                "/analyze",
                files={
                    "file": (
                        "data.xlsx",
                        sample_xlsx,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
                data={"prompt": "What is total revenue?"},
            )

        assert resp.status_code == 200
        assert resp.json()["insight"] == "Total revenue is 12500."

    def test_chat_history_forwarded(self, client, sample_csv):
        cleaning_code = "pass"
        analysis_code = "result = df['Sales'].mean()"
        insight_text = "Average sales are 150."

        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response(cleaning_code),
                _mock_ai_response(analysis_code),
                _mock_ai_response(insight_text),
            ]

            resp = client.post(
                "/analyze",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={
                    "prompt": "What about the average?",
                    "history": "user: What is total sales?\nassistant: 450",
                },
            )

        assert resp.status_code == 200
        
        # Verify the analysis prompt received the history
        calls = mock_client.chat.completions.create.call_args_list
        analysis_call_prompt = calls[1][1]["messages"][0]["content"]
        assert "450" in analysis_call_prompt

    def test_missing_file_returns_422(self, client):
        resp = client.post("/analyze", data={"prompt": "hello"})
        assert resp.status_code == 422

    def test_cleaning_failure_still_returns_insight(self, client, sample_csv):
        bad_cleaning = "raise ValueError('bad')"
        analysis_code = "result = len(df)"
        insight_text = "There are 3 rows."

        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response(bad_cleaning),
                _mock_ai_response(analysis_code),
                _mock_ai_response(insight_text),
            ]

            resp = client.post(
                "/analyze",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "How many rows?"},
            )

        assert resp.status_code == 200
        assert resp.json()["insight"] == insight_text

    def test_oversized_file_rejected(self, client, monkeypatch):
        monkeypatch.setattr("main.MAX_FILE_SIZE_BYTES", 10)

        with patch("main.client"):
            resp = client.post(
                "/analyze",
                files={"file": ("big.csv", b"x" * 100, "text/csv")},
                data={"prompt": "test"},
            )

        assert resp.status_code == 413

    def test_code_fences_stripped_from_ai_response(self, client, sample_csv):
        cleaning_code = "```python\npass\n```"
        analysis_code = "```python\nresult = 42\n```"
        insight_text = "The answer is 42."

        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response(cleaning_code),
                _mock_ai_response(analysis_code),
                _mock_ai_response(insight_text),
            ]

            resp = client.post(
                "/analyze",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "Give me a number"},
            )

        assert resp.status_code == 200
        assert resp.json()["insight"] == insight_text


class TestHealthEndpoint:
    def test_returns_healthy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "model" in data
        assert data["max_file_size_mb"] == 200
