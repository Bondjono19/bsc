from unittest.mock import AsyncMock, MagicMock
import pytest
from recognition.eventConnectionService import EventConnectionService
from shared.database.models import Event


def test_init_channel(fake_db):
    service = EventConnectionService("channelName", fake_db)
    assert service.channel == "channelName"
    assert service.redis_instance is None
    assert service.pubsub is None
    assert service.listen_task is None
    assert service.databaseManager is fake_db

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


async def test_initialize_swallows_connection_errors(monkeypatch, fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)

    async def boom(*args, **kwargs):
        raise ConnectionError("cannot reach redis")

    monkeypatch.setattr(
        "recognition.eventConnectionService.redis.from_url", boom
    )

    await service.initialize()
    assert service.redis_instance is None


async def test_close_cancels_tasks_and_closes_connections(fake_db):
    service = EventConnectionService("recognitionChannel", fake_db)
    service.publish_task = MagicMock()
    service.pubsub = AsyncMock()
    service.redis_instance = AsyncMock()

    await service.close()
    service.publish_task.cancel.assert_called_once()
    service.pubsub.close.assert_awaited_once()
    service.redis_instance.aclose.assert_awaited_once()
