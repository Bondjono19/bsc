from database.databaseManager import databaseManager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database.models.authtoken import AuthToken
from sqlalchemy import select
from database.databaseManager import databaseManager

class AuthenticationService:
    async def verifyToken(self, token: str) -> bool:
        res = await databaseManager.execute(select(AuthToken).where(AuthToken.token == token))
        if(res):
            return True
        return False
    
authenticationService = AuthenticationService()