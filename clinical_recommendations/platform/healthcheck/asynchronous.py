from __future__ import annotations

import asyncio

from clinical_recommendations.platform.healthcheck.protocol import IHealthchecker
from clinical_recommendations.platform.healthcheck.types import Healthcheck


class AsyncHealthcheck(IHealthchecker):
    """
    Implements an asyncio healtcheck service.
    Requesting healthcheck status should be as slow as the slowest
    healthcheck provider.
    """

    async def ready(self) -> dict[str, Healthcheck]:
        not_ready: dict[str, Healthcheck] = {}

        status = await asyncio.gather(*[h.ready() for _, h in self.healthers.items()])

        for name, health in zip(self.healthers.keys(), status, strict=True):
            if health:
                not_ready[name] = health

        return not_ready

    async def live(self) -> dict[str, Healthcheck]:
        not_live: dict[str, Healthcheck] = {}

        status = await asyncio.gather(*[h.live() for _, h in self.healthers.items()])

        for name, health in zip(self.healthers.keys(), status, strict=True):
            if health:
                not_live[name] = health

        return not_live
