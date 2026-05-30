import pytest
from recognition.eventConnectionService import EventConnectionService

def test_init_channel():
    service = EventConnectionService("channelName")
    assert service.channel is "channelName"
    assert service.redis_instance is None
    assert service.pubsub is None
    assert service.listen_task is None