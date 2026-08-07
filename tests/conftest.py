import os
#Set up mock DB conf
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB", "test")

from unittest.mock import MagicMock, AsyncMock
import sqlalchemy.ext.asyncio

sqlalchemy.ext.asyncio.create_async_engine = MagicMock()

import pytest


def make_async_cm(return_value):
    """Build an object usable as `async with ... as x` yielding return_value."""
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=return_value)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


class FakeSession:
    """Stand-in for an AsyncSession used inside DatabaseManager methods.

    Records what was added/deleted/merged and lets each test decide what
    `execute()` returns, so the DB layer can be exercised without Postgres.
    """

    def __init__(self, execute_result=None):
        self.added = []
        self.deleted = []
        self.merged = []
        self.committed = 0
        self.refreshed = []
        self._execute_result = execute_result

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed += 1

    async def refresh(self, obj):
        self.refreshed.append(obj)

    async def delete(self, obj):
        self.deleted.append(obj)

    async def merge(self, obj):
        self.merged.append(obj)
        return obj

    async def execute(self, query):
        return self._execute_result


def session_factory(session):
    return MagicMock(return_value=session)


@pytest.fixture
def fake_session():
    return FakeSession()


@pytest.fixture
def fake_db():

    from shared.database.databaseManager import DatabaseManager

    return AsyncMock(spec=DatabaseManager)
