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
        import pgembed
    except ImportError as exc:
        raise RuntimeError(
            "PostgreSQL is unavailable and pgembed is not installed"
        ) from exc

    import shutil

    bin_dir = Path(pgembed.__file__).parent / "pginstall" / "bin"
    initdb = bin_dir / "initdb.exe"
    pg_ctl = bin_dir / "pg_ctl.exe"
    psql = bin_dir / "psql.exe"
    if not initdb.exists() or not pg_ctl.exists():
        raise RuntimeError("pgembed PostgreSQL binaries were not found")

    data_dir = BACKEND_ROOT / ".pgdata"
    if data_dir.exists():
        try:
            subprocess.run(
                [str(pg_ctl), "-D", str(data_dir), "-m", "fast", "stop"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception:
            pass
        try:
            subprocess.run(
                ["cmd", "/c", "rmdir", "/s", "/q", str(data_dir)],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception:
            pass
        shutil.rmtree(data_dir, ignore_errors=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            str(initdb),
            "-D",
            str(data_dir),
            "--auth=trust",
            "--auth-local=trust",
            "--encoding=utf8",
            "-U",
            "postgres",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )

    port = 54329
    while True:
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                break
        port += 1

    subprocess.run(
        [
            str(pg_ctl),
            "-D",
            str(data_dir),
            "-w",
            "-o",
            f'-h "127.0.0.1" -p {port}',
            "-l",
            str(data_dir / "log"),
            "start",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )

    database_url = f"postgresql://postgres:@127.0.0.1:{port}/postgres"

    import psycopg

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.customer')")
            table_exists = cursor.fetchone()[0] is not None
    if not table_exists:
        deploy_dir = BACKEND_ROOT.parent / "data" / "db" / "db_setup"
        deploy_file = deploy_dir / "deploy.sql"
        if deploy_file.exists():
            result = subprocess.run(
                [str(psql), "-d", database_url, "-f", str(deploy_file)],
                cwd=str(deploy_dir),
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    "Embedded PostgreSQL schema deployment failed: "
                    + (result.stderr or result.stdout)[-2000:]
                )

    try:
        ensure_application_tables()
    except Exception:
        pass

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
    global _EMBEDDED_URL
    if get_engine.cache_info().currsize:
        get_engine().dispose()
        get_engine.cache_clear()
    if _EMBEDDED_URL is not None:
        try:
            import pgembed

            bin_dir = Path(pgembed.__file__).parent / "pginstall" / "bin"
            pg_ctl = bin_dir / "pg_ctl.exe"
            data_dir = BACKEND_ROOT / ".pgdata"
            if pg_ctl.exists() and data_dir.exists():
                subprocess.run(
                    [str(pg_ctl), "-D", str(data_dir), "-m", "fast", "stop"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
        except Exception:
            pass
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
    try:
        with get_engine().begin() as connection:
            connection.execute(text(statement))
    except Exception:
        return


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
