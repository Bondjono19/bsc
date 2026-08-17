from unittest.mock import MagicMock

import pytest

from shared.database.databaseManager import DatabaseManager
from shared.database.models import Identity
from tests.conftest import FakeSession, session_factory


@pytest.fixture
def manager():
    return DatabaseManager()


async def test_add_commits_refreshes_and_returns_object(manager):
    session = FakeSession()
    manager.AsyncSessionLocal = session_factory(session)

    obj = Identity(global_id=1, name="Alice")
    result = await manager.add(obj)

    assert result is obj
    assert session.added == [obj]
    assert session.committed == 1
    assert session.refreshed == [obj]

async def test_execute_returns_scalar_list(manager):
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = ["a", "b"]
    session = FakeSession(execute_result=result_mock)
    manager.AsyncSessionLocal = session_factory(session)

    rows = await manager.execute("SELECT 1")

    assert rows == ["a", "b"]

async def test_remove_deletes_when_found(manager):
    target = Identity(global_id=1, name="Bob")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = target
    session = FakeSession(execute_result=result_mock)
    manager.AsyncSessionLocal = session_factory(session)

    ok = await manager.remove(1, Identity)

    assert ok is True
    assert session.deleted == [target]
    assert session.committed == 1

async def test_remove_returns_false_when_not_found(manager):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session = FakeSession(execute_result=result_mock)
    manager.AsyncSessionLocal = session_factory(session)

    ok = await manager.remove(1234, Identity)

    assert ok is False
    assert session.deleted == []
    assert session.committed == 0

async def test_update_merges_and_commits(manager):
    session = FakeSession()
    manager.AsyncSessionLocal = session_factory(session)

    obj = Identity(global_id=1, name="Carol")
    await manager.update(obj)

    assert session.merged == [obj]
    assert session.committed == 1

async def test_fetch_all_returns_scalar_list(manager):
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = ["ident1", "ident2"]
    session = FakeSession(execute_result=result_mock)
    manager.AsyncSessionLocal = session_factory(session)

    rows = await manager.fetchAll(Identity, Identity.embeddings)

    assert rows == ["ident1", "ident2"]

async def test_add_embedding_creates_identity_when_missing(manager):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    session = FakeSession(execute_result=result_mock)
    manager.AsyncSessionLocal = session_factory(session)

    embedding = await manager.add_embedding("Dave", [0.0] * 512, global_id=77)

    identity = session.added[0]
    assert isinstance(identity, Identity)
    assert identity.name == "Dave"
    assert identity.global_id == 77
    assert session.flushed == 1
    assert embedding.identity_id == identity.id
    assert session.committed == 1

async def test_add_embedding_reuses_existing_identity(manager):
    existing = Identity(global_id=1, name="Dave")
    existing.id = 12
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = existing
    session = FakeSession(execute_result=result_mock)
    manager.AsyncSessionLocal = session_factory(session)

    embedding = await manager.add_embedding("Dave", [0.5] * 512)

    assert session.added == [embedding]
    assert session.flushed == 0
    assert embedding.identity_id == 12
