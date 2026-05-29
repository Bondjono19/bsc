import redis.asyncio as redis
import os
import asyncio
import logging
import json
from shared.database.databaseManager import databaseManager
from shared.database.models import Event
from sqlalchemy import select

class EventConnectionService:
    def __init__(self, channel: str):
        self.channel = channel
        self.redis_instance = None
        self.pubsub = None
        self.listen_task = None
        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.connectedOnPublish = None
        #self.REDIS_CERT_REQUIRED = os.getenv("REDIS_CERT_REQUIRED")
    
    async def __aenter__(self) -> "EventConnectionService":
        await self.initialize()
        print("version20.27 ECS")
        self.listen_task = asyncio.create_task(self.listen(self.channel))
        self.publish_task = asyncio.create_task(self.try_flush())
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def initialize(self) -> None:
        try:
            self.redis_instance = await redis.from_url(
                f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}", socket_connect_timeout=5
            )
            await self.redis_instance.ping()
            self.pubsub = self.redis_instance.pubsub()
        except Exception as e:
            print(e)
            print("Failed connnecting to event broker on (re)initialize")
    
    async def close(self) -> None:
        if self.listen_task:
            self.listen_task.cancel()
        if self.publish_task:
            self.publish_task.cancel()
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_instance:
            await self.redis_instance.aclose()

    async def reconnect(self) -> None:
        try:
            if self.pubsub:
                await self.pubsub.aclose()
        except:
            pass
        try:
            if self.redis_instance:
                await self.redis_instance.aclose()
        except Exception as e:
                print(e)
        print("trying reinitialize")
        await self.initialize()
    async def listen(self,channel: str) -> None:
        while True:
            try:
                if not self.redis_instance:
                    print("Error on connection to event broker, sleeping 10 and reconneting")
                    await asyncio.sleep(10)
                    await self.reconnect()
                    continue
                self.pubsub = self.redis_instance.pubsub()
                await self.pubsub.subscribe(channel)
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        await self.handleMessage(message["data"])
            except (redis.exceptions.TimeoutError, asyncio.TimeoutError):
                if(await self.redis_instance.ping()):
                    continue
                else:
                    await asyncio.sleep(10)
                    await self.reconnect()
                    print(f"Error on connection (timeout) to event broker without successful ping, sleeping 10 and reconneting:{e}")
            except Exception as e:
                    print(f"Error on connection to event broker, sleeping 10 and reconneting:{e}")
                    await asyncio.sleep(10)
                    await self.reconnect()

    async def try_flush(self) -> None:
        while True:
            try:
                eventSum = 0
                if(self.redis_instance and await self.redis_instance.ping()):
                    events = await databaseManager.execute(select(Event).where(Event.status == "pending").where(Event.direction == "outbound"))
                    for event in events:
                        try:
                            event = await self.publish(event)
                            eventSum+=1
                        except:
                            print("failed to flush event:" + str(event))
            except Exception as e:
                print(f"flushing went wrong: {e}")
            if(eventSum>0):
                print(f"Flushed {eventSum} events")
            await asyncio.sleep(30)

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
            await databaseManager.update(event)
        return event


    async def handleMessage(self,message: str) -> None:
        data = json.loads(message)
        #Handle message appropriately
        #Store event in DB
        return
        
eventConnectionService = EventConnectionService("recognitionChannel")