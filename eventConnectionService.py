import redis.asyncio as redis
import os
import asyncio
import logging
import json
from database.databaseManager import databaseManager
from database.models.event import Event
from sqlalchemy import select

class EventConnectionService:
    def __init__(self):
        self.redis_instance = None
        self.pubsub = None
        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        self.connectedOnPublish = None
        #self.REDIS_CERT_REQUIRED = os.getenv("REDIS_CERT_REQUIRED")
    
    async def initialize(self) -> None:
        self.redis_instance = await redis.from_url(
            f"rediss://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}",
            ssl_cert_reqs=None,
            decode_responses=True
        )
        self.pubsub = self.redis_instance.pubsub()

    async def listen(self,channel: str) -> None:
        while True:
            try:
                await self.pubsub.subscribe(channel)
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        await self.handleMessage(message["data"])
            except Exception as e:
                logging.error(e)
                await asyncio.sleep(5)
                await self.reconnect()

    async def reconnect(self):
        try:
            await self.pubsub.aclose()
        except:
            pass
        finally:
            await self.initialize()

    async def publish(self, event: Event) -> None:
        try:
            channel = event.channel
            message = event.content
            await self.redis_instance.publish(channel,message)
            event.status = "published"
        except:
            event.status = "pending"
        
        await databaseManager.update(event)

    async def try_flush(self):
        if(self.redis_instance.ping()):
            result = await databaseManager.execute(select(Event).where(Event.status == "pending").where(Event.direction == "outbound"))
            events = result.scalars().all()

            for event in events:
                try:
                    await self.publish(event)
                    event.status = "published"
                    await databaseManager.update(event)
                except:
                    #log
                    pass


    async def handleMessage(self,message: str) -> None:
        data = json.loads(message)
        #create some new event object
        