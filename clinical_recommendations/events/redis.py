from __future__ import annotations

from typing import AsyncGenerator

from redis.asyncio import Redis

from clinical_recommendations.events.events import (
    RecommendationEvent,
    RecommendationEventHandler,
)


class RedisEventHandler(RecommendationEventHandler):
    def __init__(self, client: Redis, channel: str = "recommendations") -> None:
        self.redis = client
        self.channel = channel

    async def send_recommendation(self, recommendation: RecommendationEvent):
        await self.redis.publish(
            self.channel, RecommendationEvent.model_dump_json(recommendation)
        )

    async def listen_for_recommendations(
        self,
    ) -> AsyncGenerator[RecommendationEvent, None]:
        async with self.redis.pubsub() as pubsub:
            await pubsub.subscribe(self.channel)

            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True)
                if not msg:
                    continue
                yield RecommendationEvent.model_validate_json(msg["data"].decode())
