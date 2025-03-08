from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from clinical_recommendations.platform.healthcheck.protocol import IHealther
from clinical_recommendations.platform.healthcheck.types import Healthcheck


async def is_online(conn: AsyncConnection) -> Healthcheck | None:
    try:
        await conn.execute(text("SELECT 1"))
    except Exception as e:
        return Healthcheck(
            message="postgreSQL database not available",
            error={"type": type(e).__name__, "message": str(e)},
        )
    return None


class PostgresHealthcheck(IHealther):
    def __init__(self, connection: AsyncConnection):
        self.conn = connection

    async def ready(self) -> Healthcheck | None:
        return await is_online(self.conn)

    async def live(self) -> Healthcheck | None:
        return await is_online(self.conn)
