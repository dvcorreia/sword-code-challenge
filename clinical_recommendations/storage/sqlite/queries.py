# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.28.0
# source: queries.sql
from __future__ import annotations

from typing import Any, Optional

import sqlalchemy
import sqlalchemy.ext.asyncio

from clinical_recommendations.storage.sqlite import models

GET_RECOMMENDATION = """-- name: get_recommendation \\:one
SELECT recommendation_id, patient_id, recommendation, timestamp FROM recommendations WHERE recommendation_id = ?
"""


INSERT_RECOMMENDATION = """-- name: insert_recommendation \\:exec
INSERT INTO recommendations (
    recommendation_id,
    patient_id,
    recommendation,
    timestamp
) VALUES (?, ?, ?, ?)
"""


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def get_recommendation(
        self, *, recommendation_id: Any
    ) -> Optional[models.Recommendation]:
        row = (
            await self._conn.execute(
                sqlalchemy.text(GET_RECOMMENDATION), {"p1": recommendation_id}
            )
        ).first()
        if row is None:
            return None
        return models.Recommendation(
            recommendation_id=row[0],
            patient_id=row[1],
            recommendation=row[2],
            timestamp=row[3],
        )

    async def insert_recommendation(
        self,
        *,
        recommendation_id: Any,
        patient_id: Any,
        recommendation: Any,
        timestamp: Any,
    ) -> None:
        await self._conn.execute(
            sqlalchemy.text(INSERT_RECOMMENDATION),
            {
                "p1": recommendation_id,
                "p2": patient_id,
                "p3": recommendation,
                "p4": timestamp,
            },
        )
