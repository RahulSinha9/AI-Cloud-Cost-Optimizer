import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .ai_advisor import AIAdvisor
from .aws_cost import CostExplorerClient
from .config import get_settings
from .detector import detect_anomalies
from .metrics import ANALYSIS_LATENCY, ANOMALIES, REQUESTS
from .models import AnalysisRequest, AnalysisResponse
from .recommender import recommend

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="AI Cloud Cost Optimizer", version="0.1.0", lifespan=lifespan)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    started = time.perf_counter()
    REQUESTS.labels("/v1/analyze").inc()
    try:
        anomalies = detect_anomalies(request.points, settings.anomaly_z_threshold)
        ANOMALIES.inc(len(anomalies))
        recommendations = recommend(
            request.points,
            anomalies,
            request.monthly_budget,
            settings.max_recommendations,
        )
        summary = await AIAdvisor(settings).refine(anomalies, recommendations, request.context)
        return AnalysisResponse(
            anomalies=anomalies, recommendations=recommendations, summary=summary
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Cost analysis failed") from exc
    finally:
        ANALYSIS_LATENCY.observe(time.perf_counter() - started)


@app.get("/v1/aws/daily", response_model=list)
def aws_daily():
    if not settings.cost_explorer_enabled:
        raise HTTPException(status_code=503, detail="AWS Cost Explorer integration is disabled")
    return CostExplorerClient(settings.aws_region).daily_costs(settings.cost_lookback_days)
