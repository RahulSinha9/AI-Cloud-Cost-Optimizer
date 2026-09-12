from statistics import mean

from .models import Anomaly, CostPoint, Recommendation


def recommend(
    points: list[CostPoint], anomalies: list[Anomaly], monthly_budget: float | None, limit: int
) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    total = sum(p.amount for p in points)
    avg_daily = mean(p.amount for p in points)
    projected_monthly = avg_daily * 30

    if monthly_budget and projected_monthly > monthly_budget:
        excess = projected_monthly - monthly_budget
        recommendations.append(
            Recommendation(
                title="Reduce non-essential spend to budget",
                priority="high",
                estimated_monthly_savings=round(excess * 0.7, 2),
                rationale=(
                    f"Projected monthly spend is {projected_monthly:.2f}, above the "
                    f"configured budget of {monthly_budget:.2f}."
                ),
                action="Review top service drivers, idle resources, and data-transfer costs before the next billing cycle.",
            )
        )

    if anomalies:
        spike = max(anomalies, key=lambda a: a.z_score)
        recommendations.append(
            Recommendation(
                title="Investigate the largest spend spike",
                priority="high" if spike.severity == "high" else "medium",
                estimated_monthly_savings=round(spike.amount * 0.25 * 30 / max(len(points), 1), 2),
                rationale=spike.reason,
                action="Compare deployment changes, autoscaling events, new managed services, and data-transfer usage for the anomaly date.",
            )
        )

    high_services = {}
    for point in points:
        high_services[point.service] = high_services.get(point.service, 0) + point.amount
    if high_services:
        service, service_total = max(high_services.items(), key=lambda item: item[1])
        share = service_total / max(total, 1)
        recommendations.append(
            Recommendation(
                title=f"Optimize {service} usage",
                priority="medium" if share >= 0.3 else "low",
                estimated_monthly_savings=round(service_total * 0.1, 2),
                rationale=f"{service} represents {share:.0%} of the analyzed spend.",
                action="Check utilization, commitment discounts, rightsizing, storage lifecycle policies, and unattached resources.",
            )
        )

    return recommendations[:limit]
