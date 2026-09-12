import json

import httpx

from .config import Settings
from .models import Anomaly, Recommendation


class AIAdvisor:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def refine(
        self,
        anomalies: list[Anomaly],
        recommendations: list[Recommendation],
        context: str,
    ) -> str:
        if not self.settings.ai_enabled:
            return self._deterministic_summary(anomalies, recommendations)

        payload = {
            "model": self.settings.ai_model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cloud FinOps advisor. Be concise, evidence-based, and avoid inventing savings.",
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "anomalies": [a.model_dump(mode="json") for a in anomalies],
                            "recommendations": [r.model_dump(mode="json") for r in recommendations],
                            "context": context,
                        }
                    ),
                },
            ],
        }
        headers = (
            {"Authorization": f"Bearer {self.settings.ai_api_key}"}
            if self.settings.ai_api_key
            else {}
        )
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.settings.ai_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            body = response.json()
        return body["choices"][0]["message"]["content"]

    @staticmethod
    def _deterministic_summary(
        anomalies: list[Anomaly], recommendations: list[Recommendation]
    ) -> str:
        if not anomalies:
            return "No statistically significant upward cost anomalies were detected in the supplied data."
        top = max(anomalies, key=lambda a: a.z_score)
        return (
            f"Detected {len(anomalies)} upward cost anomaly(ies). The largest was on {top.date}, "
            f"at {top.amount:.2f} versus a baseline of {top.baseline:.2f}. "
            f"Prioritize: {recommendations[0].title.lower()}"
            if recommendations
            else f"Detected {len(anomalies)} upward cost anomaly(ies); investigate {top.date} first."
        )
