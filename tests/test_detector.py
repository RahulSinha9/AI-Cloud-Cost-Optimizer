from datetime import date, timedelta

from app.detector import detect_anomalies
from app.models import CostPoint


def points(values):
    start = date(2026, 1, 1)
    return [CostPoint(date=start + timedelta(days=i), amount=v, service="EC2") for i, v in enumerate(values)]


def test_detects_spike():
    anomalies = detect_anomalies(points([10, 11, 10, 12, 11, 50]), z_threshold=2.0)
    assert len(anomalies) == 1
    assert anomalies[0].date == date(2026, 1, 6)


def test_returns_empty_for_constant_series():
    assert detect_anomalies(points([10, 10, 10]), z_threshold=2.0) == []
