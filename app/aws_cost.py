from datetime import date, timedelta

import boto3

from .models import CostPoint


class CostExplorerClient:
    def __init__(self, region: str):
        self.client = boto3.client("ce", region_name=region)

    def daily_costs(self, lookback_days: int) -> list[CostPoint]:
        end = date.today()
        start = end - timedelta(days=lookback_days)
        response = self.client.get_cost_and_usage(
            TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )
        points: list[CostPoint] = []
        for result in response.get("ResultsByTime", []):
            day = date.fromisoformat(result["TimePeriod"]["Start"])
            for group in result.get("Groups", []):
                amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                points.append(
                    CostPoint(date=day, amount=max(0.0, amount), service=group["Keys"][0])
                )
        return points
