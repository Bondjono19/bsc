import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest
from redis.asyncio.connection import Connection, SSLConnection
from recognition.eventConnectionService import EventConnectionService
from shared.database.models import Event


def test_init_channel(fake_db):
    service = EventConnectionService("channelName", fake_db)
    assert service.channel == "channelName"
    assert service.redis_instance is not None
    assert service.databaseManager is fake_db


def test_tls_disabled_when_env_unset(monkeypatch, fake_db):
    monkeypatch.delenv("ENABLE_TLS_REDIS", raising=False)
    service = EventConnectionService("channelName", fake_db)
    assert service.redis_instance.connection_pool.connection_class is Connection


@pytest.mark.parametrize("value", ["false", "False", "true", "True"])
def test_tls_enabled_only_when_env_is_truthy(monkeypatch, fake_db, value):
    monkeypatch.setenv("ENABLE_TLS_REDIS", value)
    service = EventConnectionService("channelName", fake_db)
    pool = service.redis_instance.connection_pool

    if value.lower() == "true":
        assert pool.connection_class is SSLConnection
        assert pool.connection_kwargs["ssl_ca_certs"] == "/certs/broker_cert.pem"
    else:
        assert pool.connection_class is Connection

async def test_publish_success_marks_published_and_persists(fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.redis_instance = AsyncMock()

    event = Event(
        direction="outbound",
        content="Detected: Messi",
        channel="recognitionChannel",
        status="pending",
    )

    result = await service.publish(event)

    assert result.status == "published"
    service.redis_instance.publish.assert_awaited_once_with(
        "recognitionChannel", "Detected: Messi"
    )
    fake_db.update.assert_awaited_once_with(event)

async def test_publish_failure_reverts_to_pending_and_raises(fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.redis_instance = AsyncMock()
    service.redis_instance.publish.side_effect = ConnectionError("broker down")

    event = Event(
        direction="outbound",
        content="msg",
        channel="recognitionChannel",
        status="pending",
    )

    with pytest.raises(ConnectionError):
        await service.publish(event)

    assert event.status == "pending"
    fake_db.update.assert_awaited_once_with(event)


async def test_try_flush_publishes_pending_events(monkeypatch, fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.redis_instance = AsyncMock()

    event = Event(
        direction="outbound",
        content="Detected: Messi",
        channel="recognitionChannel",
        status="pending",
    )
    fake_db.execute.return_value = [event]

    async def stop_after_one_iteration(_seconds):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        "recognition.eventConnectionService.asyncio.sleep", stop_after_one_iteration
    )

    with pytest.raises(asyncio.CancelledError):
        await service.try_flush()

    assert event.status == "published"
    service.redis_instance.publish.assert_awaited_once_with(
        "recognitionChannel", "Detected: Messi"
    )
    fake_db.update.assert_awaited_once_with(event)


async def test_try_flush_swallows_connection_errors(monkeypatch, fake_db, capsys):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.redis_instance = AsyncMock()
    service.redis_instance.ping.side_effect = ConnectionError("cannot reach redis")

    async def stop_after_one_iteration(_seconds):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        "recognition.eventConnectionService.asyncio.sleep", stop_after_one_iteration
    )

    with pytest.raises(asyncio.CancelledError):
        await service.try_flush()

    fake_db.execute.assert_not_awaited()
    assert "Connection error: cannot reach redis" in capsys.readouterr().out


async def test_close_cancels_tasks_and_closes_connections(fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.publish_task = MagicMock()
    service.redis_instance = AsyncMock()

    await service.close()
    service.publish_task.cancel.assert_called_once()
    service.redis_instance.aclose.assert_awaited_once()


async def test_context_manager_starts_and_cancels_flush_task(fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.redis_instance = AsyncMock()
    fake_db.execute.return_value = []

    async with service as ecs:
        assert ecs is service
        assert service.publish_task is not None
        assert not service.publish_task.done()

    await asyncio.sleep(0)
    assert service.publish_task.cancelled()
    service.redis_instance.aclose.assert_awaited_once()


async def test_close_without_started_task_is_safe(fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.redis_instance = AsyncMock()

    await service.close()

    service.redis_instance.aclose.assert_awaited_once()
