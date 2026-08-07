from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from api.authenticationService import AuthenticationService
from api.identityService import IdentityService
from shared.database.databaseManager import DatabaseManager
from api.routers import IdentityRouter

# Setup
@asynccontextmanager
async def run(app: FastAPI):
   async with databaseManager as db:
      app.state.db = db
      print("app started")
      yield
      print("app cloased")

app = FastAPI(lifespan=run)

databaseManager = DatabaseManager()
authenticationService = AuthenticationService(databaseManager)
identityService = IdentityService(databaseManager)
routingService = IdentityRouter(identityService)

app.include_router(routingService.router)


# Define middleware for checking auth
@app.middleware("http")
async def middleware(request: Request, call_next):
   token = request.headers.get("Authorization")

   token_verified = await authenticationService.verifyToken(token)

   if not (token_verified):
      return Response("Unauthorized",status_code=401)

   res = await call_next(request)

   return res

