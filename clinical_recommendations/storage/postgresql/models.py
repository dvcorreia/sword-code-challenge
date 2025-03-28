# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.28.0
from __future__ import annotations

import dataclasses
import datetime
import uuid


@dataclasses.dataclass()
class Recommendation:
    id: uuid.UUID
    patient_id: str
    timestamp: datetime.datetime


@dataclasses.dataclass()
class RecommendationItem:
    item_id: int
    recommendation_id: uuid.UUID
    text: str
