from fastapi.testclient import TestClient

from app.main import app


def test_healthz():
    with TestClient(app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze():
    with TestClient(app) as client:
        response = client.post(
            "/v1/analyze",
            json={
                "points": [
                    {"date": "2026-01-01", "amount": 10, "service": "EC2"},
                    {"date": "2026-01-02", "amount": 11, "service": "EC2"},
                    {"date": "2026-01-03", "amount": 12, "service": "EC2"},
                    {"date": "2026-01-04", "amount": 50, "service": "EC2"},
                ],
                "monthly_budget": 500,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert "anomalies" in body
    assert "recommendations" in body
    assert "summary" in body
