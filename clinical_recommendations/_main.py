from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, AsyncGenerator, Sequence
from uuid import UUID

import redis.asyncio as redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OpenIdConnect
from hypercorn import Config
from hypercorn.asyncio import serve
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from clinical_recommendations.engine.opa import OpaEngine
from clinical_recommendations.engine.recommendation import (
    ClinicalRecommendationEngine,
    PatientData,
)
from clinical_recommendations.events.events import (
    RecommendationEvent,
    RecommendationEventHandler,
)
from clinical_recommendations.events.redis import RedisEventHandler
from clinical_recommendations.storage.migrations import (
    apply_migrations_async,
    get_postgres_migrations,
)
from clinical_recommendations.storage.postgresql.queries import AsyncQuerier

recommendation_engine: ClinicalRecommendationEngine = OpaEngine(
    addr=os.environ.get("OPA_URL", "http://localhost:8181"),
    policy="clinical_recommendations.rules.recommendations",
)


def get_recommendation_engine() -> ClinicalRecommendationEngine:
    return recommendation_engine


RecommendationEngineDep = Annotated[
    ClinicalRecommendationEngine, Depends(get_recommendation_engine)
]


def postgres_uri() -> str:
    pg_host = os.environ.get("PG_HOST", "localhost")
    pg_port = os.environ.get("PG_PORT", 5432)
    pg_user = os.environ.get("PG_USER", "postgres")
    pg_password = os.environ.get("PG_PASSWORD", "mysecretpassword")
    pg_db = os.environ.get("PG_DATABASE", "recommendations")

    return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"


engine = create_async_engine(
    postgres_uri().replace("postgresql", "postgresql+asyncpg"), echo=True
)


async def get_db_conn() -> AsyncGenerator[AsyncConnection, None]:
    async with engine.begin() as conn:
        yield conn


def get_storage(conn: Annotated[AsyncConnection, Depends(get_db_conn)]) -> AsyncQuerier:
    return AsyncQuerier(conn)


StorageDep = Annotated[AsyncQuerier, Depends(get_storage)]


redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
)


def get_redis() -> redis.Redis:
    return redis_client


RedisDep = Annotated[redis.Redis, Depends(get_redis)]


def get_event_handler(redis: RedisDep) -> RecommendationEventHandler:
    return RedisEventHandler(redis)


EventHandlerDep = Annotated[RecommendationEventHandler, Depends(get_event_handler)]


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await apply_migrations_async(conn, get_postgres_migrations())
    yield
    await engine.dispose()
    await redis_client.close()


oidc = OpenIdConnect(openIdConnectUrl=os.environ.get("OIDC_URL", ""), auto_error=True)

OIDCDep = Annotated[str, Depends(oidc)]

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "clientId": os.environ.get("OIDC_CLIENT_ID", ""),
        "clientSecret": os.environ.get("OIDC_CLIENT_SECRET", ""),
        "appName": "Clinical Recommendations",
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "openid profile email",
    },
)

origins = ["*"]  # TODO: adjust for production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Recommendation(BaseModel):
    recommendation_id: UUID
    patiend_id: str
    recommendations: list[str]
    timestamp: datetime


class EvaluateRequest(BaseModel):
    patient_id: str
    data: PatientData


class EvaluateResponse(Recommendation): ...


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(
    data: EvaluateRequest,
    recommendation_engine: RecommendationEngineDep,
    storage: StorageDep,
    events: EventHandlerDep,
) -> EvaluateResponse:
    (recommendation_id, recommendations) = await recommendation_engine.recommend(
        data.data
    )

    now = datetime.now()

    try:
        await storage.insert_recommendation(
            recommendation_id=recommendation_id,
            patient_id=data.patient_id,
            timestamp=now,
            recommendations=recommendations,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save recommendation: {str(e)}"
        ) from e

    for recommendation in recommendations:
        await events.send_recommendation(
            RecommendationEvent(
                patient_id=data.patient_id,
                recommendation_id=str(recommendation_id),
                recommendation=recommendation,
                timestamp=now,
            )
        )

    return EvaluateResponse(
        recommendation_id=recommendation_id,
        patiend_id=data.patient_id,
        recommendations=recommendations,
        timestamp=now,
    )


class FetchRecommendationResponse(Recommendation): ...


@app.get(
    "/recommendation/{recommendation_id}", response_model=FetchRecommendationResponse
)
async def fetch_recommendation(
    recommendation_id: UUID, storage: StorageDep
) -> FetchRecommendationResponse:
    rows = [row async for row in storage.get_recommendation_by_id(id=recommendation_id)]

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Recommendation with ID {recommendation_id} not found",
        )

    row = rows[0]

    return FetchRecommendationResponse(
        recommendation_id=row.id,
        patiend_id=row.patient_id,
        recommendations=[r.text for r in rows],
        timestamp=row.timestamp,
    )


def main(_: Sequence[str] | None = None) -> int:
    # type issue: https://github.com/encode/starlette/discussions/2040
    asyncio.run(serve(app, hypercorn_config()))  # type: ignore[arg-type]
    return 0


def hypercorn_config() -> Config:
    config = Config()
    config.bind = ["0.0.0.0"]
    return config
