from __future__ import annotations

import httpx
from pydantic import UUID4, BaseModel

from clinical_recommendations.engine.recommendation import (
    ClinicalRecommendationEngine,
    PatientData,
    Recommendation,
)


class RecommendationRequest(BaseModel):
    input: PatientData


class RecommendationResponse(BaseModel):
    decision_id: UUID4
    result: list[Recommendation]


class OpaEngine(ClinicalRecommendationEngine):
    def __init__(self, addr: str, policy: str) -> None:
        self.url = f"{addr}/v1/data/{policy.replace('.', '/')}"

    async def recommend(self, data: PatientData) -> list[Recommendation]:
        body = RecommendationRequest(input=data)
        async with httpx.AsyncClient() as client:
            r = await client.post(self.url, json=body.model_dump())
        r.raise_for_status()
        recommendation = RecommendationResponse.model_validate(r.json())
        return recommendation.result
