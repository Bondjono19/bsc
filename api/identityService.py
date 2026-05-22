from shared.database.databaseManager import databaseManager
from sqlalchemy import insert
from shared.database.models import Identity,Embedding
from typing import Type
import logging
import json

class IdentityService:
    async def addIdentity(self, global_id: str, name: str, embeddings: list[list[float]]) -> Identity:
        try:
            embedding_objs = []
            for embedding in embeddings:
                embedding_objs.append(Embedding(vector=embedding))
            identity = Identity(global_id=global_id,name=name,embeddings=embedding_objs)
            identity = await databaseManager.add(identity)
            print(identity)
            return identity
        except Exception as e:
            logging.error(e)
            return None
        
    async def removeIdentity(self,identityId: int) -> bool:
        return await databaseManager.remove(identityId,Identity)
        
identityService = IdentityService()
