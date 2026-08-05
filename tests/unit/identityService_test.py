from unittest.mock import AsyncMock

from api.identityService import identityService
from shared.database.models import Identity


async def test_add_identity_with_embeddings(monkeypatch):
    captured = {}

    async def fake_add(obj):
        captured["obj"] = obj
        obj.id = 42
        return obj

    monkeypatch.setattr("api.identityService.databaseManager.add", fake_add)

    result = await identityService.addIdentity(
        global_id="00001234", name="John Doe", embeddings=[[0.0] * 512, [1.0] * 512]
    )

    assert result.id == 42
    added = captured["obj"]
    assert isinstance(added, Identity)
    assert added.name == "John Doe"
    assert added.global_id == "00001234"
    assert len(added.embeddings) == 2
    assert added.embeddings[0].vector == [0.0] * 512


async def test_add_identity_without_embeddings(monkeypatch):
    captured = {}

    async def fake_add(obj):
        captured["obj"] = obj
        return obj

    monkeypatch.setattr("api.identityService.databaseManager.add", fake_add)

    result = await identityService.addIdentity(
        global_id="55", name="No Embeds", embeddings=None
    )

    assert result is captured["obj"]
    assert result.embeddings == []


async def test_add_identity_returns_none_on_db_error(monkeypatch):
    add = AsyncMock(side_effect=RuntimeError("unique violation"))
    monkeypatch.setattr("api.identityService.databaseManager.add", add)

    result = await identityService.addIdentity("1", "dup", [[0.0] * 512])

    assert result is None


async def test_remove_identity_delegates_to_db(monkeypatch):
    remove = AsyncMock(return_value=True)
    monkeypatch.setattr("api.identityService.databaseManager.remove", remove)

    assert await identityService.removeIdentity(7) is True
    remove.assert_awaited_once_with(7, Identity)


async def test_remove_identity_returns_false_when_missing(monkeypatch):
    remove = AsyncMock(return_value=False)
    monkeypatch.setattr("api.identityService.databaseManager.remove", remove)

    assert await identityService.removeIdentity(999) is False
