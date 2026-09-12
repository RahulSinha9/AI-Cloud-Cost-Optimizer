from fastapi.testclient import TestClient

from app.main import app


def test_ready_and_metrics():
    with TestClient(app) as client:
        assert client.get("/readyz").status_code == 200
        metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "cost_optimizer_requests_total" in metrics.text
