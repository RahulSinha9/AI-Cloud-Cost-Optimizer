from statistics import mean, pstdev

from .models import Anomaly, CostPoint


def detect_anomalies(points: list[CostPoint], z_threshold: float = 2.5) -> list[Anomaly]:
    ordered = sorted(points, key=lambda x: x.date)
    if len(ordered) < 3:
        return []

    amounts = [p.amount for p in ordered]
    baseline = mean(amounts)
    deviation = pstdev(amounts)
    if deviation == 0:
        return []

    anomalies: list[Anomaly] = []
    for point in ordered:
        z_score = (point.amount - baseline) / deviation
        if z_score < z_threshold:
            continue
        severity = "high" if z_score >= 4 else "medium" if z_score >= 3 else "low"
        anomalies.append(
            Anomaly(
                date=point.date,
                amount=point.amount,
                baseline=round(baseline, 2),
                z_score=round(z_score, 2),
                severity=severity,
                reason=(
                    f"{point.service} spend of {point.amount:.2f} is "
                    f"{z_score:.2f} standard deviations above the observed baseline."
                ),
            )
        )
    return anomalies
