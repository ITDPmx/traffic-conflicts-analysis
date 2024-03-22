from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from ngsildclient import Entity, AsyncClient, iso8601
import sys
import uuid
from datetime import datetime

client = AsyncClient(hostname = "ec2-13-59-97-182.us-east-2.compute.amazonaws.com",
                        port = 1027) 
print("connected")
app = FastAPI()

#---------------------------------------------------------------------------------------------------------------------------------
@app.post("/update")
async def update_entity(request:Request)->None:
    entity = await request.json()
    await client.update(entity)


#---------------------------------------------------------------------------------------------------------------------------------
@app.post("/ent2infer")
async def ent2infer() -> list:
    """
    This method gets a list of entities pending to infer

    Args:
        None
    Returns:
        entities [list]: a list with entities with False infered attribute
    """
    #get all the camera entities
    cam_e = await client.query(type="cameraObserved")
    #filter camera entities that have not been infered
    cam_e_f =  [e for e in cam_e if e['infered'].value == False]
    #bye
    return JSONResponse(status_code=201, content=jsonable_encoder(cam_e_f))

    #return cam_e_f
    

#---------------------------------------------------------------------------------------------------------------------------------
@app.post("/create_person")
async def create_person_entity(request: Request):
    """
    This method create person entity
    Args:
        person [dict]
    Returns:
        entity [Entity]
    """      
    person = await request.json()
    id = uuid.uuid4()
    e = Entity("personObserved", f"{person['id']}:{id}")
    e.obs()
    date = iso8601.from_datetime(datetime.fromtimestamp(person["timestamps"][0]))
    e.prop("coordinates", person["coordinates"], observedat=date)
    e.prop("geo_coordinates", person["geo_coordinates"])
    e.prop("timestamps", person["timestamps"])
    e.prop("activity", person["activity"])
    e.rel("camera", person["camera"])
    await client.upsert(e)
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(e.to_dict()),
                        headers={"Content-Location": client.entities.to_broker_url(e)})
#---------------------------------------------------------------------------------------------------------------------------------
@app.post("/homography")
async def get_homography(request: Request) -> list:
    """
    This method get the homography attribute from calibration entity of the source.
    Args:
        Entity [Entity]
    Returns:
        homography [list]
    """
    camera =  await request.json()
    #mapeo para que el id coincida en el front
    map_front = {'1': '1', '2':'0'}
    calibration_data = await client.get('urn:ngsi-ld:calibrations:' + map_front[camera['root']['id'].split(':')[3]])
    #bye
    return JSONResponse(status_code=201,
                        content=jsonable_encoder(calibration_data['homography'].value),
                        headers={"Content-Location": client.entities.to_broker_url(calibration_data)})
