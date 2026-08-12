from shared.database.databaseManager import DatabaseManager
from shared.database.models import Identity,Embedding
import logging

class IdentityService:
    def __init__(self,databaseManager: DatabaseManager) -> None:
        self.databaseManager = databaseManager
        
    async def addIdentity(self, global_id: str, name: str, embeddings: list[list[float]]) -> Identity:
        try:
            if not embeddings == None:
                embedding_objs = []
                for embedding in embeddings:
                    embedding_objs.append(Embedding(vector=embedding))
                identity = Identity(global_id=global_id,name=name,embeddings=embedding_objs)
            else:
                identity = Identity(global_id=global_id,name=name)
            identity = await self.databaseManager.add(identity)
            return identity
        except Exception as e:
            logging.error(e)
            return None
        
    async def removeIdentity(self,identityId: int) -> bool:
        return await self.databaseManager.remove(identityId,Identity)
        
