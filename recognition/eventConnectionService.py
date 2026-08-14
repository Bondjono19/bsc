import redis.asyncio as redis
import os
import asyncio
from shared.database.databaseManager import DatabaseManager
from shared.database.models import Event
from sqlalchemy import select

class EventConnectionService:
    def __init__(self, channel: str,database_manager: DatabaseManager) -> None:
        self.channel = channel
        self.redis_instance = None
        self.publish_task = None
        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.databaseManager = database_manager
        self.redis_instance = redis.from_url(f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}", socket_connect_timeout=5)
        #self.REDIS_CERT_REQUIRED = os.getenv("REDIS_CERT_REQUIRED")
    
    async def __aenter__(self) -> "EventConnectionService":
        self.publish_task = asyncio.create_task(self.try_flush())
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
    
    async def close(self) -> None:
        if self.publish_task:
            self.publish_task.cancel()
        if self.redis_instance:
            await self.redis_instance.aclose()

    async def publish(self, event: Event) -> Event:
        try:
            channel = event.channel
            message = event.content
            await self.redis_instance.publish(channel,message)
            event.status = "published"
        except Exception:
            event.status = "pending"
            raise
        finally:
            await self.databaseManager.update(event)
        return event

    async def try_flush(self) -> None:
        while True:
            try:
                eventSum = 0
                await self.redis_instance.ping()
                events = await self.databaseManager.execute(select(Event).where(Event.status == "pending").where(Event.direction == "outbound"))
                for event in events:
                    try:
                        event = await self.publish(event)
                        eventSum+=1
                    except:
                        print("failed to flush event:" + str(event))
            except Exception as e:
                print(f"Connection error: {e}")
            if(eventSum>0):
                print(f"Flushed {eventSum} events")
            await asyncio.sleep(30)
