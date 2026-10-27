import asyncio
from collections.abc import Mapping
from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.shared.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
    )


def dispose_engine() -> None:
    if get_engine.cache_info().currsize:
        get_engine().dispose()
        get_engine.cache_clear()


def _fetch_all(
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    with get_engine().connect() as connection:
        result = connection.execute(text(statement), parameters or {})
        return [dict(row) for row in result.mappings()]


def _fetch_one(
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    with get_engine().connect() as connection:
        row = (
            connection.execute(
                text(statement),
                parameters or {},
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None


async def fetch_all(
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(_fetch_all, statement, parameters)


async def fetch_one(
    statement: str,
    parameters: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    return await asyncio.to_thread(_fetch_one, statement, parameters)
