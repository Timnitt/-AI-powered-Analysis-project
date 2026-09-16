"""Tests for the /data-quality endpoint."""

import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd


class TestDataQualityEndpoint:
    def test_returns_row_and_column_counts(self, client, sample_csv):
        resp = client.post(
            "/data-quality",
            files={"file": ("data.csv", sample_csv, "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows"] == 3
        assert data["columns"] == 3

    def test_detects_no_issues_on_clean_data(self, client, sample_csv):
        resp = client.post(
            "/data-quality",
            files={"file": ("data.csv", sample_csv, "text/csv")},
        )
        data = resp.json()
        assert data["duplicate_rows"] == 0
        assert data["nulls"] == {}

    def test_detects_missing_values(self, client):
        df = pd.DataFrame({
            "A": [1, None, 3],
            "B": ["x", "y", None],
        })
        buf = io.BytesIO()
        df.to_csv(buf, index=False)
        csv_bytes = buf.getvalue()

        resp = client.post(
            "/data-quality",
            files={"file": ("nulls.csv", csv_bytes, "text/csv")},
        )
        data = resp.json()
        assert "A" in data["nulls"]
        assert data["nulls"]["A"]["count"] == 1
        assert "B" in data["nulls"]

    def test_detects_duplicate_rows(self, client):
        df = pd.DataFrame({
            "X": [1, 1, 2],
            "Y": ["a", "a", "b"],
        })
        buf = io.BytesIO()
        df.to_csv(buf, index=False)
        csv_bytes = buf.getvalue()

        resp = client.post(
            "/data-quality",
            files={"file": ("dupes.csv", csv_bytes, "text/csv")},
        )
        data = resp.json()
        assert data["duplicate_rows"] == 1

    def test_detects_outliers(self, client):
        values = [10, 11, 12, 10, 11, 12, 10, 11, 100]
        df = pd.DataFrame({"Val": values})
        buf = io.BytesIO()
        df.to_csv(buf, index=False)
        csv_bytes = buf.getvalue()

        resp = client.post(
            "/data-quality",
            files={"file": ("outlier.csv", csv_bytes, "text/csv")},
        )
        data = resp.json()
        assert "Val" in data["outliers"]
        assert data["outliers"]["Val"] >= 1

    def test_returns_dtypes(self, client, sample_csv):
        resp = client.post(
            "/data-quality",
            files={"file": ("data.csv", sample_csv, "text/csv")},
        )
        data = resp.json()
        assert "Product" in data["dtypes"]
        assert "Sales" in data["dtypes"]

    def test_returns_preview(self, client, sample_csv):
        resp = client.post(
            "/data-quality",
            files={"file": ("data.csv", sample_csv, "text/csv")},
        )
        data = resp.json()
        assert len(data["preview"]) == 3
        assert "Product" in data["preview"][0]

    def test_returns_issues_summary(self, client):
        df = pd.DataFrame({
            "A": [1, None, 1],
            "B": [1, 2, 1],
        })
        buf = io.BytesIO()
        df.to_csv(buf, index=False)
        csv_bytes = buf.getvalue()

        resp = client.post(
            "/data-quality",
            files={"file": ("issues.csv", csv_bytes, "text/csv")},
        )
        data = resp.json()
        assert any("missing" in i for i in data["issues"])
        assert any("duplicate" in i for i in data["issues"])

    def test_xlsx_file_works(self, client, sample_xlsx):
        resp = client.post(
            "/data-quality",
            files={
                "file": (
                    "data.xlsx",
                    sample_xlsx,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["rows"] == 3
