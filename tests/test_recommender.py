from datetime import date, timedelta

from app.models import CostPoint
from app.recommender import recommend


def test_budget_recommendation():
    points = [CostPoint(date=date(2026, 1, i + 1), amount=100) for i in range(7)]
    recs = recommend(points, [], monthly_budget=2000, limit=10)
    assert any("budget" in r.title.lower() for r in recs)


def test_top_service_recommendation():
    points = [
        CostPoint(date=date(2026, 1, 1), amount=100, service="EC2"),
        CostPoint(date=date(2026, 1, 2), amount=20, service="S3"),
        CostPoint(date=date(2026, 1, 3), amount=120, service="EC2"),
    ]
    recs = recommend(points, [], None, 10)
    assert any("EC2" in r.title for r in recs)
