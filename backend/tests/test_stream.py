"""Tests for the /analyze-stream SSE endpoint."""

import json
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _mock_ai_response(content: str):
    choice = MagicMock()
    choice.message.content = content
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _parse_sse_events(response):
    events = []
    for line in response.text.strip().split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


class TestAnalyzeStreamEndpoint:
    def test_streams_all_stages(self, client, sample_csv):
        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response("pass"),
                _mock_ai_response("result = df['Sales'].sum()"),
                _mock_ai_response("Total sales are 450."),
                _mock_ai_response("fig, ax = plt.subplots()\nax.bar(['A'], [1])"),
            ]

            resp = client.post(
                "/analyze-stream",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "What is total sales?"},
            )

        assert resp.status_code == 200
        events = _parse_sse_events(resp)

        stages = [e["stage"] for e in events]
        assert stages[0] == "Cleaning data"
        assert stages[1] == "Running analysis"
        assert stages[2] == "Generating insight"
        assert stages[3] == "Creating chart"
        assert stages[4] == "complete"

    def test_returns_insight_in_final_event(self, client, sample_csv):
        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response("pass"),
                _mock_ai_response("result = 42"),
                _mock_ai_response("The answer is 42."),
                _mock_ai_response("fig, ax = plt.subplots()\nax.bar(['A'], [1])"),
            ]

            resp = client.post(
                "/analyze-stream",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "Give me a number"},
            )

        events = _parse_sse_events(resp)
        final = events[-1]
        assert final["stage"] == "complete"
        assert final["insight"] == "The answer is 42."

    def test_includes_step_numbers(self, client, sample_csv):
        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response("pass"),
                _mock_ai_response("result = 1"),
                _mock_ai_response("One."),
                _mock_ai_response("fig, ax = plt.subplots()\nax.bar(['A'], [1])"),
            ]

            resp = client.post(
                "/analyze-stream",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "test"},
            )

        events = _parse_sse_events(resp)
        progress_events = [e for e in events if "step" in e]
        assert len(progress_events) == 4
        assert progress_events[0]["step"] == 1
        assert progress_events[3]["step"] == 4
        assert all(e["total"] == 4 for e in progress_events)

    def test_cached_skips_cleaning(self, client, sample_csv):
        """Second request with same file uses cache: 3 steps, not 4."""
        from main import _clean_cache

        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response("pass"),
                _mock_ai_response("result = 1"),
                _mock_ai_response("First."),
                _mock_ai_response("fig, ax = plt.subplots()\nax.bar(['A'], [1])"),
            ]
            client.post(
                "/analyze-stream",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "first"},
            )

        assert len(_clean_cache) == 1

        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response("result = 2"),
                _mock_ai_response("Second."),
                _mock_ai_response("fig, ax = plt.subplots()\nax.bar(['B'], [2])"),
            ]
            resp = client.post(
                "/analyze-stream",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "second"},
            )

        events = _parse_sse_events(resp)
        stages = [e["stage"] for e in events]
        assert stages[0] == "Using cached clean data"
        assert events[0].get("cached") is True
        assert stages[1] == "Running analysis"
        assert stages[2] == "Generating insight"
        assert stages[3] == "Creating chart"
        assert stages[4] == "complete"

        progress_events = [e for e in events if e.get("step", -1) > 0]
        assert all(e["total"] == 3 for e in progress_events)

        assert events[-1]["insight"] == "Second."

    def test_chart_failure_still_completes(self, client, sample_csv):
        with patch("main.client") as mock_client:
            mock_client.chat.completions.create.side_effect = [
                _mock_ai_response("pass"),
                _mock_ai_response("result = 99"),
                _mock_ai_response("Ninety-nine."),
                _mock_ai_response("raise ValueError('bad chart')"),
            ]

            resp = client.post(
                "/analyze-stream",
                files={"file": ("data.csv", sample_csv, "text/csv")},
                data={"prompt": "test"},
            )

        events = _parse_sse_events(resp)
        final = events[-1]
        assert final["stage"] == "complete"
        assert final["insight"] == "Ninety-nine."
        assert final["chart"] is None

    def test_oversized_file_rejected(self, client, monkeypatch):
        monkeypatch.setattr("main.MAX_FILE_SIZE_BYTES", 10)

        with patch("main.client"):
            resp = client.post(
                "/analyze-stream",
                files={"file": ("big.csv", b"x" * 100, "text/csv")},
                data={"prompt": "test"},
            )

        assert resp.status_code == 413
