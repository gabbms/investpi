from fastapi.testclient import TestClient

from app.main import app


def test_saude():
    assert TestClient(app).get("/api/saude").json() == {"ok": True}
