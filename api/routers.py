from fastapi import APIRouter,Request,Response
from api.identityService import IdentityService
from api.utils.embeddingVectorParser import parseEmbedding
import json


class IdentityRouter:
    def __init__(self,identityService: IdentityService):
        self.identityService = identityService
        self.router = APIRouter(prefix="/identities")
        self.router.add_api_route("/create",self.addIdentity)
        self.router.add_api_route("/remove",self.removeIdentity)

    async def addIdentity(self,request: Request):
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
    
        name = data.get("name")
        if not name:
            return Response("Missing name", status_code=400)
    
        global_id = data.get("globalid")
        if not global_id:
            return Response("Missing globalid", status_code=400)
    
        embeddings = data.get("embeddings")

        if not parseEmbedding(embeddings=embeddings):
            return Response("Invalid vector(s)", status_code=400)
        res = await self.identityService.addIdentity(data["globalid"], data["name"],embeddings)
        if(res):
            return {"message":"Successfully added embedding", "id":res.id}
        else:
            return Response("Error adding embedding", status_code=500)
    


    async def removeIdentity(self,request: Request):
        '''
            JSON struct:
                {
                    "id" : 123
                }
        '''
        data = json.loads(await request.body())
        if not data:
            return Response("Empty request body", status_code=400)
        id = data.get("id")
        if not id:
            return Response("Missing id", status_code=400)
        res = await self.identityService.removeIdentity(id)
        if not res:
            return Response("No such identity", status_code=400)
        return Response("Removed identity succesfully", status_code=200)

