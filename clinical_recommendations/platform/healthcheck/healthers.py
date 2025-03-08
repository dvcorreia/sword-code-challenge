from __future__ import annotations

from typing import Awaitable, Callable, Self

from clinical_recommendations.platform.healthcheck.protocol import IHealther
from clinical_recommendations.platform.healthcheck.types import Healthcheck


class _healther_func(IHealther):
    def __init__(
        self: Self,
        live_func: Callable[[], Awaitable[Healthcheck | None]],
        ready_func: Callable[[], Awaitable[Healthcheck | None]],
    ) -> None:
        self._livef = live_func
        self._readyf = ready_func

    async def ready(self) -> Healthcheck | None:
        return await self._readyf()

    async def live(self) -> Healthcheck | None:
        return await self._livef()


def health_func(
    f: Callable[[], Awaitable[Healthcheck | None]],
    *,
    live: bool = True,
    ready: bool = True,
) -> IHealther:
    async def ok():
        return None

    hfunc = _healther_func(f, f)

    if not live:
        hfunc._livef = ok

    if not ready:
        hfunc._readyf = ok

    return hfunc
