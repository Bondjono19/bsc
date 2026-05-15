from database.databaseManager import databaseManager
from database.models import AuthToken
from sqlalchemy import select
from database.databaseManager import databaseManager

class AuthenticationService:
    async def verifyToken(self, token: str) -> bool:
        stripToken = lambda token: token.split()[1]
        try:
            stripped_token = stripToken(token)
            print(stripped_token)
        except:
            return False
        res = await databaseManager.execute(select(AuthToken).where(AuthToken.token == stripped_token))
        if(res):
            return True
        return False
    
authenticationService = AuthenticationService()