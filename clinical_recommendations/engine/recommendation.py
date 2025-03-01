from __future__ import annotations

from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field


class PatientData(BaseModel):
    age: int = Field(gt=0)
    has_chronic_pain: bool
    bmi: int = Field(gt=0)
    recent_surgery: bool


class ClinicalRecommendationEngine(Protocol):
    async def recommend(self, data: PatientData) -> tuple[UUID, list[str]]: ...
