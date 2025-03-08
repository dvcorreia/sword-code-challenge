from __future__ import annotations

from redis.asyncio import Redis

from clinical_recommendations.platform.healthcheck.protocol import IHealther
from clinical_recommendations.platform.healthcheck.types import Healthcheck


async def is_online(rc: Redis) -> Healthcheck | None:
    try:
        response = await rc.ping()
    except Exception as e:
        return Healthcheck(
            message="redis service not available",
            error={"type": type(e).__name__, "message": str(e)},
        )
    if not response:
        return Healthcheck(
            message="redis service not responding properly",
            error={"response": response},
        )
    return None


class RedisHealthcheck(IHealther):
    def __init__(self, client: Redis):
        self.rc = client

    async def ready(self) -> Healthcheck | None:
        return await is_online(self.rc)

    async def live(self) -> Healthcheck | None:
        return await is_online(self.rc)
