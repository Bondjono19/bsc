from fastapi import FastAPI, Request, Response
from authenticationService import authenticationService
from database.databaseManager import databaseManager
# Setup
app = FastAPI()

await databaseManager.initializeDatabase()


# Define middleware for checking auth
@app.middleware("http")
async def middleware(request: Request, call_next):
    token = request.headers.get("Authorization")

    token_verified = await authenticationService.verifyToken(token)

    if not (token_verified):
       return Response("Unauthorized",status_code=401)

    res = await call_next(request)

    return res



