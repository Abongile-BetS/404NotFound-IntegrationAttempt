"""Seed the local database using the existing SQL seed files."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = Path(__file__).resolve().parent
SEED_DIR = PROJECT_ROOT / "data" / "db" / "seed"
NORMALIZED_LOAD = PROJECT_ROOT / "data" / "etl" / "src" / "normalized_load.py"


def database_url() -> str:
    sys.path.insert(0, str(BACKEND_ROOT))
    from app.shared.database.connection import get_engine

    return str(get_engine().url)


def psql_path() -> str:
    found = shutil.which("psql")
    if found:
        return found
    try:
        import pgembed

        candidate = Path(pgembed.__file__).parent / "pginstall" / "bin" / "psql.exe"
        if candidate.exists():
            return str(candidate)
    except ImportError:
        pass
    raise SystemExit("psql was not found; install PostgreSQL client tools or pgembed")


def run_seed(seed_file: Path) -> None:
    subprocess.run(
        [
            psql_path(),
            "-d",
            database_url(),
            "-c",
            "TRUNCATE TABLE raw.iovation CASCADE;",
        ],
        check=False,
    )
    result = subprocess.run(
        [psql_path(), "-d", database_url(), "-f", str(seed_file)],
        cwd=str(SEED_DIR),
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"Seeding failed while running {seed_file}")


def main() -> None:
    seed_file = SEED_DIR / "iovation_seed_100.sql"
    print(f"Loading seed data from {seed_file}...")
    run_seed(seed_file)

    from urllib.parse import urlparse

    parsed = urlparse(database_url())
    env = dict(os.environ)
    env["PGHOST"] = parsed.hostname or "localhost"
    env["PGPORT"] = str(parsed.port or 5432)
    env["PGDATABASE"] = (parsed.path or "/postgres").lstrip("/")
    env["PGUSER"] = parsed.username or "postgres"
    env["PGPASSWORD"] = parsed.password or ""

    print("Running normalized load ETL...")
    result = subprocess.run(
        [sys.executable, str(NORMALIZED_LOAD)],
        cwd=str(PROJECT_ROOT),
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Normalized load failed")

    print("Seeding completed.")

    sys.path.insert(0, str(BACKEND_ROOT))
    from app.shared.database.connection import dispose_engine

    dispose_engine()


if __name__ == "__main__":
    main()
