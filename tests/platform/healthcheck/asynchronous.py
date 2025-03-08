from __future__ import annotations

import asyncio
from datetime import timedelta

from clinical_recommendations.platform.healthcheck.protocol import IHealther
from clinical_recommendations.platform.healthcheck.types import Healthcheck


class AsyncHealtherMock(IHealther):
    def __init__(
        self,
        sleep_time: timedelta,
        live_status: str | None,
        ready_status: str | None,
    ) -> None:
        self.sleep_time = sleep_time
        self.live_status = live_status
        self.ready_status = ready_status

    async def live(self) -> Healthcheck | None:
        await asyncio.sleep(self.sleep_time.total_seconds())

        if self.live_status is None:
            return None

        return Healthcheck(message=self.live_status)

    async def ready(self) -> Healthcheck | None:
        await asyncio.sleep(self.sleep_time.total_seconds())

        if self.ready_status is None:
            return None

        return Healthcheck(message=self.ready_status)
