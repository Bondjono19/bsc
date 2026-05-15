from database.databaseManager import databaseManager
from sqlalchemy import insert
from database.models import Identity
from typing import Type
import logging
import json

class IdentityService:
    async def addIdentity(self, embedding: list[float], name: str) -> Identity:
        try:
            identity = Identity(name=name,embedding=embedding)
            identity = await databaseManager.add(identity)
            return identity
        except Exception as e:
            logging.error(e)
            return None
        
    async def removeIdentity(self,identityId: int) -> bool:
        return await databaseManager.remove(identityId,Identity)
        
identityService = IdentityService()