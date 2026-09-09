import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:8501")

    from main import app

    return TestClient(app)


@pytest.fixture()
def sample_csv() -> bytes:
    df = pd.DataFrame(
        {
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Sales": [100, 200, 150],
            "Profit": [20, -10, 35],
        }
    )
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


@pytest.fixture()
def sample_xlsx() -> bytes:
    df = pd.DataFrame(
        {
            "Region": ["North", "South", "East"],
            "Revenue": [5000, 3000, 4500],
        }
    )
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()
