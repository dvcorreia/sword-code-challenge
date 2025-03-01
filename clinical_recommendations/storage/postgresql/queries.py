# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.28.0
# source: queries.sql
from __future__ import annotations

import dataclasses
import datetime
import uuid
from typing import AsyncIterator, Iterator, List

import sqlalchemy
import sqlalchemy.ext.asyncio


GET_RECOMMENDATION_BY_ID = """-- name: get_recommendation_by_id \\:many
SELECT r.id, r.patient_id, r.timestamp, ri.item_id, ri.text
FROM recommendations r
JOIN recommendation_items ri ON r.id = ri.recommendation_id
WHERE r.id = :p1
"""


@dataclasses.dataclass()
class GetRecommendationByIDRow:
    id: uuid.UUID
    patient_id: str
    timestamp: datetime.datetime
    item_id: int
    text: str


INSERT_RECOMMENDATION = """-- name: insert_recommendation \\:exec
WITH recommendation_insert AS (
    INSERT INTO recommendations (
        id,
        patient_id,
        timestamp
    ) VALUES (:p1, :p2, :p3)
)
INSERT INTO recommendation_items (
    recommendation_id,
    text
) SELECT :p1, unnest(:p4\\:\\:text[]) as text
"""


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def get_recommendation_by_id(
        self, *, id: uuid.UUID
    ) -> Iterator[GetRecommendationByIDRow]:
        result = self._conn.execute(
            sqlalchemy.text(GET_RECOMMENDATION_BY_ID), {"p1": id}
        )
        for row in result:
            yield GetRecommendationByIDRow(
                id=row[0],
                patient_id=row[1],
                timestamp=row[2],
                item_id=row[3],
                text=row[4],
            )

    def insert_recommendation(
        self,
        *,
        recommendation_id: uuid.UUID,
        patient_id: str,
        timestamp: datetime.datetime,
        recommendations: List[str],
    ) -> None:
        self._conn.execute(
            sqlalchemy.text(INSERT_RECOMMENDATION),
            {
                "p1": recommendation_id,
                "p2": patient_id,
                "p3": timestamp,
                "p4": recommendations,
            },
        )


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def get_recommendation_by_id(
        self, *, id: uuid.UUID
    ) -> AsyncIterator[GetRecommendationByIDRow]:
        result = await self._conn.stream(
            sqlalchemy.text(GET_RECOMMENDATION_BY_ID), {"p1": id}
        )
        async for row in result:
            yield GetRecommendationByIDRow(
                id=row[0],
                patient_id=row[1],
                timestamp=row[2],
                item_id=row[3],
                text=row[4],
            )

    async def insert_recommendation(
        self,
        *,
        recommendation_id: uuid.UUID,
        patient_id: str,
        timestamp: datetime.datetime,
        recommendations: List[str],
    ) -> None:
        await self._conn.execute(
            sqlalchemy.text(INSERT_RECOMMENDATION),
            {
                "p1": recommendation_id,
                "p2": patient_id,
                "p3": timestamp,
                "p4": recommendations,
            },
        )
