from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from api.main import app, authenticationService


@pytest_asyncio.fixture
async def client(monkeypatch):
    """AsyncClient bound to the real ASGI app.

    ASGITransport does not run the FastAPI lifespan, so the app's
    databaseManager startup never touches Postgres. Auth is allowed by
    default; individual tests can override verifyToken to test rejection.
    """
    monkeypatch.setattr(
        authenticationService, "verifyToken", AsyncMock(return_value=True)
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac


AUTH_HEADERS = {"Authorization": "Bearer test-token"}
