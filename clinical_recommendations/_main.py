from __future__ import annotations

import asyncio
from typing import Sequence

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from hypercorn import Config
from hypercorn.asyncio import serve

app = FastAPI()


@app.post("/evaluate")
async def evaluate(_: Request) -> Response:
    raise HTTPException(status_code=501)


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
