from __future__ import annotations

from datetime import datetime
from typing import AsyncGenerator, Protocol

from pydantic import BaseModel


class RecommendationEvent(BaseModel):
    patient_id: str
    recommendation_id: str
    recommendation: str
    timestamp: datetime


class RecommendationEventHandler(Protocol):
    async def send_recommendation(self, recommendation: RecommendationEvent): ...
    async def listen_for_recommendations(
        self,
    ) -> AsyncGenerator[RecommendationEvent, None]: ...
