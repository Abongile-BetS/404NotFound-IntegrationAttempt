import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from app.shared.database import connection


class DatabaseConnectionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        with self.engine.begin() as database:
            database.execute(
                text("CREATE TABLE sample (id INTEGER PRIMARY KEY, name TEXT)")
            )
            database.execute(
                text("INSERT INTO sample (id, name) VALUES (:id, :name)"),
                {"id": 1, "name": "sample"},
            )

        self.engine_patch = patch.object(
            connection,
            "get_engine",
            return_value=self.engine,
        )
        self.engine_patch.start()

    async def asyncTearDown(self):
        self.engine_patch.stop()
        self.engine.dispose()

    async def test_fetch_all_returns_rows_and_binds_parameters(self):
        rows = await connection.fetch_all(
            "SELECT id, name FROM sample WHERE id = :id",
            {"id": 1},
        )

        self.assertEqual(rows, [{"id": 1, "name": "sample"}])

    async def test_fetch_one_returns_matching_row(self):
        row = await connection.fetch_one(
            "SELECT id, name FROM sample WHERE id = :id",
            {"id": 1},
        )

        self.assertEqual(row, {"id": 1, "name": "sample"})

    async def test_fetch_one_returns_none_when_no_row_matches(self):
        row = await connection.fetch_one(
            "SELECT id, name FROM sample WHERE id = :id",
            {"id": 2},
        )

        self.assertIsNone(row)
