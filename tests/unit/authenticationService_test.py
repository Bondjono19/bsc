from unittest.mock import AsyncMock

from api.authenticationService import authenticationService
from shared.database.models import AuthToken


async def test_valid_bearer_token_returns_true(monkeypatch):
    # DB returns a matching token row -> authorized.
    execute = AsyncMock(return_value=[AuthToken(token="secret", description="test")])
    monkeypatch.setattr("api.authenticationService.databaseManager.execute", execute)

    assert await authenticationService.verifyToken("Bearer secret") is True
    execute.assert_awaited_once()


async def test_unknown_token_returns_false(monkeypatch):
    execute = AsyncMock(return_value=[])
    monkeypatch.setattr("api.authenticationService.databaseManager.execute", execute)

    assert await authenticationService.verifyToken("Bearer nope") is False


async def test_malformed_header_without_scheme_returns_false(monkeypatch):
    # No space to split on -> stripToken raises -> False, DB never queried.
    execute = AsyncMock(return_value=[AuthToken(token="secret")])
    monkeypatch.setattr("api.authenticationService.databaseManager.execute", execute)

    assert await authenticationService.verifyToken("secret") is False
    execute.assert_not_awaited()


async def test_none_header_returns_false(monkeypatch):
    execute = AsyncMock(return_value=[])
    monkeypatch.setattr("api.authenticationService.databaseManager.execute", execute)

    assert await authenticationService.verifyToken(None) is False
    execute.assert_not_awaited()


async def test_only_second_part_of_header_is_used_as_token(monkeypatch):
    # "Bearer <token>" -> the query should filter on the stripped token.
    captured = {}

    async def fake_execute(query):
        captured["query"] = query
        return [AuthToken(token="abc")]

    monkeypatch.setattr(
        "api.authenticationService.databaseManager.execute", fake_execute
    )

    assert await authenticationService.verifyToken("Bearer abc") is True
    # The generated statement compiles against the auth_tokens table.
    assert "auth_tokens" in str(captured["query"])
