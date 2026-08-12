import json
from unittest.mock import AsyncMock

import pytest

from api.main import authenticationService, identityService
from tests.integration.conftest import AUTH_HEADERS


class _FakeIdentity:
    def __init__(self, id):
        self.id = id

async def test_request_without_auth_header_is_rejected(client, monkeypatch):
    monkeypatch.setattr(
        authenticationService, "verifyToken", AsyncMock(return_value=False)
    )
    resp = await client.post("/identities/create", content=json.dumps({}))
    assert resp.status_code == 401


async def test_valid_token_passes_middleware(client, monkeypatch):
    monkeypatch.setattr(
        identityService, "addIdentity", AsyncMock(return_value=_FakeIdentity(1))
    )
    resp = await client.post(
        "/identities/create",
        headers=AUTH_HEADERS,
        content=json.dumps({"name": "A", "globalid": "1"}),
    )
    assert resp.status_code == 200

async def test_create_identity_success(client, monkeypatch):
    add = AsyncMock(return_value=_FakeIdentity(99))
    monkeypatch.setattr(identityService, "addIdentity", add)

    body = {"name": "John Doe", "globalid": "00001234", "embeddings": None}
    resp = await client.post(
        "/identities/create", headers=AUTH_HEADERS, content=json.dumps(body)
    )

    assert resp.status_code == 200
    assert resp.json() == {"message": "Successfully added embedding", "id": 99}
    add.assert_awaited_once_with("00001234", "John Doe", None)

async def test_create_identity_missing_name(client):
    body = {"globalid": "1"}
    resp = await client.post(
        "/identities/create", headers=AUTH_HEADERS, content=json.dumps(body)
    )
    assert resp.status_code == 400
    assert resp.text == "Missing name"

async def test_create_identity_missing_globalid(client):
    body = {"name": "John"}
    resp = await client.post(
        "/identities/create", headers=AUTH_HEADERS, content=json.dumps(body)
    )
    assert resp.status_code == 400
    assert resp.text == "Missing globalid"

async def test_create_identity_invalid_embeddings(client):
    body = {"name": "John", "globalid": "1", "embeddings": [[0.0, 0.1, 0.2]]}
    resp = await client.post(
        "/identities/create", headers=AUTH_HEADERS, content=json.dumps(body)
    )
    assert resp.status_code == 400
    assert resp.text == "Invalid vector(s)"

async def test_create_identity_db_failure_returns_500(client, monkeypatch):
    monkeypatch.setattr(
        identityService, "addIdentity", AsyncMock(return_value=None)
    )
    body = {"name": "John", "globalid": "1"}
    resp = await client.post(
        "/identities/create", headers=AUTH_HEADERS, content=json.dumps(body)
    )
    assert resp.status_code == 500
    assert resp.text == "Error adding embedding"

async def test_create_identity_valid_512_embeddings(client, monkeypatch):
    add = AsyncMock(return_value=_FakeIdentity(5))
    monkeypatch.setattr(identityService, "addIdentity", add)

    embeddings = [[0.0] * 512]
    body = {"name": "Jane", "globalid": "7", "embeddings": embeddings}
    resp = await client.post(
        "/identities/create", headers=AUTH_HEADERS, content=json.dumps(body)
    )

    assert resp.status_code == 200
    add.assert_awaited_once_with("7", "Jane", embeddings)

async def test_remove_identity_success(client, monkeypatch):
    remove = AsyncMock(return_value=True)
    monkeypatch.setattr(identityService, "removeIdentity", remove)

    resp = await client.request(
        "DELETE", "/identities/remove", headers=AUTH_HEADERS,
        content=json.dumps({"id": 123}),
    )

    assert resp.status_code == 200
    assert resp.text == "Removed identity succesfully"
    remove.assert_awaited_once_with(123)

async def test_remove_identity_missing_id(client):
    resp = await client.request(
        "DELETE", "/identities/remove", headers=AUTH_HEADERS,
        content=json.dumps({"other": "field"}),
    )
    assert resp.status_code == 400
    assert resp.text == "Missing id"

async def test_remove_identity_empty_body(client):
    resp = await client.request(
        "DELETE", "/identities/remove", headers=AUTH_HEADERS,
        content=json.dumps({}),
    )
    assert resp.status_code == 400
    assert resp.text == "Empty request body"

async def test_remove_identity_not_found(client, monkeypatch):
    monkeypatch.setattr(
        identityService, "removeIdentity", AsyncMock(return_value=False)
    )
    resp = await client.request(
        "DELETE", "/identities/remove", headers=AUTH_HEADERS,
        content=json.dumps({"id": 999}),
    )
    assert resp.status_code == 400
    assert resp.text == "No such identity"
