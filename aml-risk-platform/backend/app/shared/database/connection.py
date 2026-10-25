import asyncio
import os
from functools import lru_cache
from typing import Any, Mapping

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


@lru_cache
def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set to connect to PostgreSQL")
    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def _fetch_all(
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    with get_engine().connect() as connection:
        result = connection.execute(text(statement), parameters or {})
        return [dict(row) for row in result.mappings()]


async def fetch_all(
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(_fetch_all, statement, parameters)


async def fetch_one(
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    rows = await fetch_all(statement, parameters)
    return rows[0] if rows else None
