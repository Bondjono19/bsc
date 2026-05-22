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
        self.lisen_task = None
        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.connectedOnPublish = None
        #self.REDIS_CERT_REQUIRED = os.getenv("REDIS_CERT_REQUIRED")
    
    async def __aenter__(self):
        print("hello")
        await self.initialize()
        self.listen_task = asyncio.create_task(self.listen(self.channel))
        self.publish_task = asyncio.create_task(self.try_flush())

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def initialize(self) -> None:
        try:
            self.redis_instance = await redis.from_url(
                f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
            )
            self.pubsub = self.redis_instance.pubsub()
        except:
            print("Failed connnecting to event broker on (re)initialize")
            pass
            #log
    
    async def close(self):
        self.listen_task.cancel()
        self.publish_task
        await self.pubsub.close()
        await self.redis_instance.aclose()

    async def reconnect(self):
        try:
            await self.pubsub.aclose()
        except:
            pass
        finally:
            print("Trying reconnect")
            await self.initialize()
            if(await self.redis_instance.ping()):
                print("Connectionn reached on ping")

    async def listen(self,channel: str) -> None:
        while True:
            try:
                await self.pubsub.subscribe(channel)
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        await self.handleMessage(message["data"])
            except Exception as e:
                logging.error(e)
                print("Error on connection to event broker, sleeping 5 and reconneting")
                await asyncio.sleep(5)
                await self.reconnect()

    async def try_flush(self):
        while True:
            if(await self.redis_instance.ping()):
                events = await databaseManager.execute(select(Event).where(Event.status == "pending").where(Event.direction == "outbound"))
                eventSum = 0
                for event in events:
                    try:
                        event = await self.publish(event)
                        await databaseManager.update(event)
                        eventSum+=1
                    except:
                        #log
                        print("Failed to flush event")
            if(eventSum>0):
                print(f"Flushed {eventSum} events")
            await asyncio.sleep(30)

    async def publish(self, event: Event) -> None:
        try:
            channel = event.channel
            message = event.content
            await self.redis_instance.publish(channel,message)
            event.status = "published"
        except:
            event.status = "pending"
        
        await databaseManager.update(event)
        return event


    async def handleMessage(self,message: str) -> None:
        data = json.loads(message)
        #create some new event object
        
eventConnectionService = EventConnectionService("someChannel")