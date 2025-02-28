from __future__ import annotations

from importlib import resources
from pathlib import Path

import sqlalchemy
import sqlalchemy.ext.asyncio


async def apply_migrations_async(conn: sqlalchemy.ext.asyncio.AsyncConnection):
    files = _get_package_migrations()

    for file in files:
        with open(file, "r") as fd:
            blob = fd.read()
        raw_conn = await conn.get_raw_connection()
        # The asyncpg sqlalchemy adapter uses a prepared statement cache which can't handle the migration statements
        await raw_conn._connection.execute(blob)  # type: ignore


def _get_package_migrations():
    migration_files = []

    with resources.path(
        "clinical_recommendations.storage.sqlite", "migrations"
    ) as migrations_dir:
        for file in sorted(Path(migrations_dir).glob("*.up.sql")):
            migration_files.append(file)

    return migration_files
