from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from api.authenticationService import authenticationService
from shared.database.databaseManager import databaseManager
from api.routers import identity_router
# Setup

@asynccontextmanager
async def run(app: FastAPI):
   async with databaseManager as db:
      app.state.db = db
      print("app started")
      yield
      print("app cloased")

app = FastAPI(lifespan=run)

app.include_router(identity_router)

# Define middleware for checking auth
@app.middleware("http")
async def middleware(request: Request, call_next):
   token = request.headers.get("Authorization")

   token_verified = await authenticationService.verifyToken(token)

   if not (token_verified):
      return Response("Unauthorized",status_code=401)

   res = await call_next(request)

   return res
