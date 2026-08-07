import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.database.databaseManager import DatabaseManager
from recognition.eventConnectionService import EventConnectionService
from recognition.recognitionService import RecognitionService
from recognition.utils.access_grantor_loader import load_access_grantor_impl

@asynccontextmanager
async def run(app: FastAPI):
    
    databaseManager = DatabaseManager()
    access_grantor = load_access_grantor_impl()
    recognitionService = RecognitionService(detection_mode=True,access_grantor=access_grantor)
    eventConnectionService = EventConnectionService("recognitionChannel")

    async with databaseManager as db, eventConnectionService as ecs,recognitionService as rs:
        app.state.db = db
        app.state.ecs = ecs
        app.state.rs = rs
        print("Started Recognition Inference App")
        yield
        print("Stopped Recognition Inference APP")

app = FastAPI(lifespan=run)