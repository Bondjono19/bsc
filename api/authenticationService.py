from shared.database.models import AuthToken
from sqlalchemy import select
from shared.database.databaseManager import DatabaseManager
import hashlib

class AuthenticationService:
    def __init__(self, databaseManager: DatabaseManager) -> None:
        self.databaseManager = DatabaseManager
    async def verifyToken(self, token: str) -> bool:
        stripToken = lambda token: token.split()[1]
        try:
            stripped_token = stripToken(token)
            print(stripped_token)
        except:
            return False
        hashed_token = hashlib.sha256(stripped_token.encode()).hexdigest()
        res = await self.databaseManager.execute(select(AuthToken).where(AuthToken.token == hashed_token))
        if(res):
            return True
        return False
    