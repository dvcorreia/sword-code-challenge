from __future__ import annotations

import asyncio
from enum import Enum

from fastapi import APIRouter, FastAPI, Response, status
from fastapi.responses import JSONResponse

from clinical_recommendations.platform.healthcheck.protocol import IHealthchecker
from clinical_recommendations.platform.healthcheck.types import Healthcheck


def add_healthcheck_handlers(
    app: FastAPI,
    healthchecker: IHealthchecker,
    *,
    prefix: str = "/healthz",
    tags: list[str | Enum] | None = None,
) -> None:
    router = APIRouter(
        prefix=prefix,
        tags=tags,
    )

    @router.get("/", response_model=dict[str, Healthcheck])
    async def _() -> Response:
        async with asyncio.TaskGroup() as tg:
            dead = tg.create_task(healthchecker.live())
            not_ready = tg.create_task(healthchecker.ready())

        # TODO: ready values overwrite live values
        healths = dead.result() | not_ready.result()

        if len(healths.keys()) > 0:
            body = {k: v.dict() for (k, v) in healths.items()}
            return JSONResponse(body, status.HTTP_503_SERVICE_UNAVAILABLE)

        return JSONResponse(None, status.HTTP_200_OK)

    @router.get("/live", response_model=dict[str, Healthcheck])
    async def _() -> Response:
        dead = await healthchecker.live()

        if len(dead.keys()) > 0:
            body = {k: v.dict() for (k, v) in dead.items()}
            return JSONResponse(body, status.HTTP_503_SERVICE_UNAVAILABLE)

        return JSONResponse(None, status.HTTP_200_OK)

    @router.get("/ready", response_model=dict[str, Healthcheck])
    async def _() -> Response:
        not_ready = await healthchecker.ready()

        if len(not_ready.keys()) > 0:
            body = {k: v.dict() for (k, v) in not_ready.items()}
            return JSONResponse(body, status.HTTP_503_SERVICE_UNAVAILABLE)

        return JSONResponse(None, status.HTTP_200_OK)

    app.include_router(router)
