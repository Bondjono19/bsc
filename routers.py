from fastapi import APIRouter,Request,Response
from identityService import identityService
from utils.embeddingVectorParser import parseEmbedding
from eventConnectionService import eventConnectionService
import json
from database.models import Event
from database.databaseManager import databaseManager
identity_router = APIRouter(prefix="/identities")

@identity_router.post("/create")
async def addIdentity(request: Request):
    data = json.loads(await request.body())
    if not data:
        return Response("Empty request body", status_code=400)
    embedding = data.get("embedding")
    if not embedding:
        return Response("Missing embedding", status_code=400)
    name = data.get("name")
    if not name:
        return Response("Missing name", status_code=400)
    if not parseEmbedding(embedding=embedding):
        return Response("Invalid vector", status_code=400)
    res = await identityService.addIdentity(data["embedding"], data["name"])
    if(res):
        return {"message":"Successfully added embedding", "id":res.id}
    else:
        return Response("Error adding embedding", status_code=500)
    


@identity_router.delete("/remove")
async def removeIdentity(request: Request):
    data = json.loads(await request.body())
    if not data:
        return Response("Empty request body", status_code=400)
    id = data.get("id")
    if not id:
        return Response("Missing id", status_code=400)
    res = await identityService.removeIdentity(id)
    if not res:
        return Response("No such identity", status_code=400)
    return Response("Removed identity succesfully", status_code=200)

@identity_router.get("/test")
async def test(req: Request):
    await databaseManager.add(Event(direction="outbound",content="lol",channel="c"))
    return {"success"}
