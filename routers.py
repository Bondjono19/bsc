from fastapi import APIRouter,Request,Response
from identityService import identityService
from utils.embeddingVectorParser import parseEmbedding
import json
identity_router = APIRouter(prefix="/identities")

@identity_router.post("/create")
async def addIdentity(request: Request):
    data = json.loads(await request.body())
    if not data:
        return Response("Empty request body", status_code=400)
    embedding = data.get("embedding")
    if not embedding:
        return Response("Missing embedding", status_code=400)
    if not parseEmbedding(embedding=embedding):
        return Response("Invalid vector", status_code=400)
    return await identityService.addIdentity(data["embedding"])
    


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

