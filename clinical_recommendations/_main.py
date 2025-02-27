from __future__ import annotations

import asyncio
from typing import Sequence, TypeAlias

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from hypercorn import Config
from hypercorn.asyncio import serve

from clinical_recommendations.engine.opa import OpaEngine
from clinical_recommendations.engine.recommendation import (
    ClinicalRecommendationEngine,
    PatientData,
    Recommendation,
)

app = FastAPI()

recommendation_engine: ClinicalRecommendationEngine = OpaEngine(
    addr="http://localhost:8181",
    policy="clinical_recommendations.rules.recommendations",
)


class EvaluateRequest(PatientData): ...


def handle_evaluate(recommendation_engine: ClinicalRecommendationEngine):
    async def evaluate(data: EvaluateRequest) -> list[Recommendation]:
        recommendations = await recommendation_engine.recommend(data)
        return recommendations

    return evaluate


@app.post("/evaluate")
async def evaluate(data: EvaluateRequest) -> list[Recommendation]:
    return await handle_evaluate(recommendation_engine)(data)


@app.get("/recommendation/{recommendation_id}")
async def fetch_recommendation(_: Request) -> Response:
    raise HTTPException(status_code=501)


def main(_: Sequence[str] | None = None) -> int:
    # type issue: https://github.com/encode/starlette/discussions/2040
    asyncio.run(serve(app, hypercorn_config()))  # type: ignore[arg-type]
    return 0


def hypercorn_config() -> Config:
    config = Config()
    config.bind = ["0.0.0.0"]
    return config
