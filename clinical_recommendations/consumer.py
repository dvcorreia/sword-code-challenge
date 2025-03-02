from __future__ import annotations

import logging
import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path
from typing import Protocol, Sequence

import duckdb
import redis.asyncio as redis

from clinical_recommendations.events.redis import RecommendationEvent, RedisEventHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clinical-recommendations-logger")


class RecommendationsLogger(Protocol):
    def log_recommendation(self, recommendation: RecommendationEvent): ...


CREATE_RECOMMENDATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS recommendations (
    patient_id VARCHAR,
    recommendation_id VARCHAR,
    recommendation VARCHAR,
    timestamp TIMESTAMP
);
"""

LOG_RECOMMENDATION = """
INSERT INTO recommendations (patient_id, recommendation_id, recommendation, timestamp)
VALUES (?, ?, ?, ?);
"""


class DuckDBRecommendationsLogger(RecommendationsLogger):
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self.conn = conn
        self.conn.execute(CREATE_RECOMMENDATIONS_TABLE)

    def log_recommendation(self, recommendation: RecommendationEvent):
        self.conn.execute(
            LOG_RECOMMENDATION,
            [
                recommendation.patient_id,
                recommendation.recommendation_id,
                recommendation.recommendation,
                recommendation.timestamp,
            ],
        )


async def _main(argv: Sequence[str] | None = None) -> int:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--redis-host",
        default=os.environ.get("REDIS_HOST", "localhost"),
        type=str,
    )

    parser.add_argument(
        "--redis-port",
        default=int(os.environ.get("REDIS_PORT", "6379")),
        type=int,
    )

    parser.add_argument(
        "--duckdb",
        default="recommendations-logging-db.duckdb",
        type=str,
        help="duckdb database file",
    )

    args = parser.parse_args(argv)

    duckdb_conn = duckdb.connect(Path(args.duckdb))
    recommendation_logger: RecommendationsLogger = DuckDBRecommendationsLogger(
        duckdb_conn
    )

    redis_client = redis.Redis(
        host=args.redis_host,
        port=args.redis_port,
    )

    event_handler = RedisEventHandler(redis_client)

    try:
        logger.info("listenning for recommendations...")
        async for event in event_handler.listen_for_recommendations():
            recommendation_logger.log_recommendation(event)
            logger.info(f"saved recommendation: {event.recommendation_id}")
    except KeyboardInterrupt:
        pass
    finally:
        await redis_client.close()
        duckdb_conn.close()

    return 0


def main():
    import asyncio

    asyncio.run(_main())


if __name__ == "__main__":
    main()
