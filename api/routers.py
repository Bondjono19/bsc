from fastapi import APIRouter,Request,Response
from api.identityService import identityService
from api.utils.embeddingVectorParser import parseEmbedding
from recognition.eventConnectionService import eventConnectionService
import json
from shared.database.models import Event
from shared.database.databaseManager import databaseManager
identity_router = APIRouter(prefix="/identities")

@identity_router.post("/create")
async def addIdentity(request: Request):
    '''
        JSON struct:
            {
                "name": "John Doe"
                "globalid": "00001234"
                "embeddings": [
                    [v1_1,v1_2,...v1_512],
                    [vi_1,vi_2,...vi_512],
                    ...
                ]
            }
    '''
    data = json.loads(await request.body())
    if not data:
        return Response("Empty request body", status_code=400)
    embeddings = data.get("embeddings")
    if not embeddings:
        return Response("Missing embedding", status_code=400)
    name = data.get("name")
    if not name:
        return Response("Missing name", status_code=400)
    if not parseEmbedding(embeddings=embeddings):
        return Response("Invalid vector(s)", status_code=400)
    global_id = data.get("globalid")
    if not global_id:
        return Response("Missing globalid", status_code=400)
    res = await identityService.addIdentity(data["globalid"], data["name"],data["embeddings"])
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
