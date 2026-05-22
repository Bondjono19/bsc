import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.database.databaseManager import databaseManager
from recognition.eventConnectionService import eventConnectionService
from recognition.recognitionService import recognitionService


@asynccontextmanager
async def run(app: FastAPI):
    async with databaseManager as db, eventConnectionService as ecs,recognitionService as rs:
        app.state.db = db
        app.state.ecs = ecs
        app.state.rs = rs
        print("Started Recognition Inference App")
        yield
        print("Stopped Recognition Inference APP")

app = FastAPI(lifespan=run)