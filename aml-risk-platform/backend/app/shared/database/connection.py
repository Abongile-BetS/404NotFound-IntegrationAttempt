import asyncio
import subprocess
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.shared.config import get_settings

BACKEND_ROOT = Path(__file__).resolve().parents[3]
_EMBEDDED_SERVER = None
_EMBEDDED_URL = None


def _postgres_available() -> bool:
    try:
        settings = get_settings()
    except Exception:
        return False
    try:
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2},
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


def _deploy_embedded_schema(database_url: str) -> None:
    project_root = BACKEND_ROOT.parent
    deploy_dir = project_root / "data" / "db" / "db_setup"
    deploy_file = deploy_dir / "deploy.sql"
    if not deploy_file.exists():
        raise RuntimeError(f"Embedded database schema file not found: {deploy_file}")

    try:
        import pgembed
    except ImportError as exc:
        raise RuntimeError(
            "PostgreSQL is unavailable and pgembed is not installed"
        ) from exc

    psql_path = Path(pgembed.__file__).parent / "pginstall" / "bin" / "psql.exe"
    if not psql_path.exists():
        psql_path = Path("psql")

    result = subprocess.run(
        [str(psql_path), "-d", database_url, "-f", str(deploy_file)],
        cwd=str(deploy_dir),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Embedded PostgreSQL schema deployment failed: "
            + (result.stderr or result.stdout)[-2000:]
        )


def _start_embedded_postgres() -> str:
    global _EMBEDDED_SERVER, _EMBEDDED_URL
    if _EMBEDDED_URL is not None:
        return _EMBEDDED_URL

    try:
        from pgembed import get_server
    except ImportError as exc:
        raise RuntimeError(
            "PostgreSQL is unavailable and pgembed is not installed"
        ) from exc

    data_dir = BACKEND_ROOT / ".pgdata"
    data_dir.mkdir(parents=True, exist_ok=True)
    server = get_server(str(data_dir), cleanup_mode="stop")
    server.ensure_pgdata_inited()
    server.ensure_postgres_running()
    database_url = server.get_uri()

    import psycopg

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.customer')")
            table_exists = cursor.fetchone()[0] is not None
    if not table_exists:
        _deploy_embedded_schema(database_url)

    _EMBEDDED_SERVER = server
    _EMBEDDED_URL = database_url
    return database_url


@lru_cache
def get_engine() -> Engine:
    if _postgres_available():
        return create_engine(
            get_settings().database_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2},
        )
    return create_engine(
        _start_embedded_postgres(),
        pool_pre_ping=True,
    )


def dispose_engine() -> None:
    global _EMBEDDED_SERVER, _EMBEDDED_URL
    if get_engine.cache_info().currsize:
        get_engine().dispose()
        get_engine.cache_clear()
    if _EMBEDDED_SERVER is not None:
        try:
            _EMBEDDED_SERVER.cleanup()
        except Exception:
            pass
        _EMBEDDED_SERVER = None
        _EMBEDDED_URL = None


def ensure_application_tables() -> None:
    statement = """
    CREATE TABLE IF NOT EXISTS public.investigation_case (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        case_guid UUID NOT NULL UNIQUE,
        fk_customer_id BIGINT REFERENCES public.customer(id),
        fk_alert_id BIGINT REFERENCES public.alert(id),
        title VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'OPEN',
        priority VARCHAR(50),
        assigned_to VARCHAR(255),
        outcome VARCHAR(255),
        notes TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS public.ai_report (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        report_guid UUID NOT NULL UNIQUE,
        fk_customer_id BIGINT REFERENCES public.customer(id),
        report_text TEXT NOT NULL,
        model VARCHAR(255),
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """
    with get_engine().begin() as connection:
        connection.execute(text(statement))


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
