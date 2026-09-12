from datetime import date

import pytest

from app.ai_advisor import AIAdvisor
from app.aws_cost import CostExplorerClient
from app.config import Settings
from app.models import Anomaly, Recommendation


@pytest.mark.asyncio
async def test_ai_fallback_summary_when_disabled():
    settings = Settings(ai_enabled=False)
    anomalies = [Anomaly(date=date(2026, 1, 2), amount=20, baseline=10, z_score=3.0, severity="medium", reason="spike")]
    recs = [Recommendation(title="Investigate", priority="high", estimated_monthly_savings=10, rationale="spike", action="check")]
    summary = await AIAdvisor(settings).refine(anomalies, recs, "")
    assert "Detected 1" in summary
    assert "2026-01-02" in summary


def test_cost_explorer_maps_grouped_results(monkeypatch):
    class FakeClient:
        def get_cost_and_usage(self, **kwargs):
            assert kwargs["Granularity"] == "DAILY"
            return {
                "ResultsByTime": [
                    {
                        "TimePeriod": {"Start": "2026-08-01", "End": "2026-08-02"},
                        "Groups": [
                            {"Keys": ["Amazon EC2"], "Metrics": {"UnblendedCost": {"Amount": "12.50"}}}
                        ],
                    }
                ]
            }

    monkeypatch.setattr("boto3.client", lambda *args, **kwargs: FakeClient())
    points = CostExplorerClient("ap-south-1").daily_costs(7)
    assert points[0].date == date(2026, 8, 1)
    assert points[0].amount == 12.5
    assert points[0].service == "Amazon EC2"
