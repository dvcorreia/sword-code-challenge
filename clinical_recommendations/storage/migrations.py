from __future__ import annotations

from importlib import resources
from pathlib import Path

import sqlalchemy
import sqlalchemy.ext.asyncio


def apply_migrations(conn: sqlalchemy.engine.Connection, paths: list[Path]):
    for file in paths:
        with open(file, "r") as fd:
            blob = fd.read()
        stmts = blob.split(";")
        for stmt in stmts:
            if stmt.strip():
                conn.execute(sqlalchemy.text(stmt))


async def apply_migrations_async(
    conn: sqlalchemy.ext.asyncio.AsyncConnection, paths: list[Path]
):
    for file in paths:
        with open(file, "r") as fd:
            blob = fd.read()
            statements = [stmt.strip() for stmt in blob.split(";") if stmt.strip()]
        raw_conn = await conn.get_raw_connection()
        for statement in statements:
            if not statement:
                continue
            await raw_conn._connection.execute(statement + ";")  # type: ignore


def get_postgres_migrations() -> list[Path]:
    return _get_package_migrations("clinical_recommendations.storage.postgresql")


def get_sqlite_migrations() -> list[Path]:
    return _get_package_migrations("clinical_recommendations.storage.sqlite")


def _get_package_migrations(package: resources.Package) -> list[Path]:
    migration_files = []

    with resources.path(package, "migrations") as migrations_dir:
        for file in sorted(Path(migrations_dir).glob("*.up.sql")):
            migration_files.append(file)

    return migration_files
