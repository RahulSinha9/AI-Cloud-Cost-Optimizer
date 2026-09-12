from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CostPoint(BaseModel):
    date: date
    amount: float = Field(ge=0)
    service: str = "unknown"
    account: str = "unknown"


class CostSeries(BaseModel):
    points: list[CostPoint]


class Anomaly(BaseModel):
    date: date
    amount: float
    baseline: float
    z_score: float
    severity: Literal["low", "medium", "high"]
    reason: str


class Recommendation(BaseModel):
    title: str
    priority: Literal["low", "medium", "high"]
    estimated_monthly_savings: float = Field(ge=0)
    rationale: str
    action: str


class AnalysisRequest(BaseModel):
    points: list[CostPoint] = Field(min_length=3)
    monthly_budget: float | None = Field(default=None, gt=0)
    context: str = ""


class AnalysisResponse(BaseModel):
    anomalies: list[Anomaly]
    recommendations: list[Recommendation]
    summary: str
