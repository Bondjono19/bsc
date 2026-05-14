from database.databaseManager import databaseManager
from sqlalchemy import insert
from database.models.identity import Identity
from typing import Type

class IdentityService:
    async def addIdentity(self, embedding: str, name: str) -> Identity:
        try:
            identity = Identity(name=name,embedding=embedding)
            identity = await databaseManager.add(identity)
            return identity
        except:
            #log
            return None
        
    async def removeIdentity(self,identityId: int) -> bool:
        return await databaseManager.remove(identityId,Type[Identity])
        
identityService = IdentityService()