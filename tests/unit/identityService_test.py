from unittest.mock import AsyncMock

from api.identityService import IdentityService
from shared.database.models import Identity


async def test_add_identity_with_embeddings(fake_db):
    captured = {}

    async def fake_add(obj):
        captured["obj"] = obj
        obj.id = 42
        return obj

    fake_db.add = fake_add
    service = IdentityService(fake_db)

    result = await service.addIdentity(
        global_id="00001234", name="John Doe", embeddings=[[0.0] * 512, [1.0] * 512]
    )

    assert result.id == 42
    added = captured["obj"]
    assert isinstance(added, Identity)
    assert added.name == "John Doe"
    assert added.global_id == "00001234"
    assert len(added.embeddings) == 2
    assert added.embeddings[0].vector == [0.0] * 512


async def test_add_identity_without_embeddings(fake_db):
    captured = {}

    async def fake_add(obj):
        captured["obj"] = obj
        return obj

    fake_db.add = fake_add
    service = IdentityService(fake_db)

    result = await service.addIdentity(
        global_id="55", name="No Embeds", embeddings=None
    )

    assert result is captured["obj"]
    assert result.embeddings == []


async def test_add_identity_returns_none_on_db_error(fake_db):
    fake_db.add = AsyncMock(side_effect=RuntimeError("unique violation"))
    service = IdentityService(fake_db)

    result = await service.addIdentity("1", "dup", [[0.0] * 512])

    assert result is None


async def test_remove_identity_delegates_to_db(fake_db):
    fake_db.remove = AsyncMock(return_value=True)
    service = IdentityService(fake_db)

    assert await service.removeIdentity(7) is True
    fake_db.remove.assert_awaited_once_with(7, Identity)


async def test_remove_identity_returns_false_when_missing(fake_db):
    fake_db.remove = AsyncMock(return_value=False)
    service = IdentityService(fake_db)

    assert await service.removeIdentity(999) is False
