from unittest.mock import AsyncMock

from api.authenticationService import AuthenticationService
from shared.database.models import AuthToken


async def test_valid_bearer_token_returns_true(fake_db):
    fake_db.execute = AsyncMock(
        return_value=[AuthToken(token="secret", description="test")]
    )
    service = AuthenticationService(fake_db)

    assert await service.verifyToken("Bearer secret") is True
    fake_db.execute.assert_awaited_once()

async def test_unknown_token_returns_false(fake_db):
    fake_db.execute = AsyncMock(return_value=[])
    service = AuthenticationService(fake_db)

    assert await service.verifyToken("Bearer nope") is False

async def test_malformed_header_without_scheme_returns_false(fake_db):
    fake_db.execute = AsyncMock(return_value=[AuthToken(token="secret")])
    service = AuthenticationService(fake_db)

    assert await service.verifyToken("secret") is False
    fake_db.execute.assert_not_awaited()

async def test_none_header_returns_false(fake_db):
    fake_db.execute = AsyncMock(return_value=[])
    service = AuthenticationService(fake_db)

    assert await service.verifyToken(None) is False
    fake_db.execute.assert_not_awaited()

async def test_only_second_part_of_header_is_used_as_token(fake_db):
    captured = {}

    async def fake_execute(query):
        captured["query"] = query
        return [AuthToken(token="abc")]

    fake_db.execute = fake_execute
    service = AuthenticationService(fake_db)

    assert await service.verifyToken("Bearer abc") is True
    assert "auth_tokens" in str(captured["query"])
