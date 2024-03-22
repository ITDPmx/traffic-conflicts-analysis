from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from ngsildclient import Entity, AsyncClient, iso8601
from mongodb import get_database
from data import *
from datetime import datetime
from bson.objectid import ObjectId
import json
import cv2
import numpy as np
from itertools import chain


MIN_NUM_POINTS = 4
ACTIVITIES = ['running', 'reading', 'playing', 'walking']

origins = ['https://expansionurbana-crowd-counting-4vn30yjdl-agrptec.vercel.app']

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = AsyncClient(hostname = "ec2-54-197-209-124.compute-1.amazonaws.com", port=1027, port_temporal=1026)

def build_camera_entity(camera: dict) -> Entity:
    e = Entity("cameraObserved", f"{camera['id']}:{iso8601.utcnow()}")
    e.obs()
    e.prop("bucket", camera["bucket"])
    e.prop("file", camera["file"])
    e.prop("timestamp", camera["timestamp"])
    e.prop("infered", False)
    return e


def build_person_entity(person: dict) -> Entity:
    e = Entity("personObserved", f"{person['id']}:{iso8601.utcnow()}")
    e.obs()
    date = iso8601.from_datetime(datetime.fromtimestamp(person["timestamps"][0]))
    e.prop("coordinates", person["coordinates"], observedat=date)
    e.prop("geo_coordinates", person["geo_coordinates"])
    e.prop("timestamps", person["timestamps"])
    e.prop("activity", person["activity"])
    e.rel("camera", person["camera"])
    return e


def build_calibration_entity(camera: dict) -> Entity:
    e = Entity("calibrations", camera['id'])
    e.obs()
    e.prop("source_points", camera["source_points"])
    e.prop("target_points", camera["target_points"])
    e.prop("homography", camera["homography"])
    return e



@app.post("/camera_footage")
async def create_entity(request: Request):
    payload = await request.json()
    entity = build_camera_entity(payload)
    await client.upsert(entity)
    return JSONResponse(status_code=201, content=jsonable_encoder(entity.to_dict()), headers={"Content-Location": client.entities.to_broker_url(entity)})


@app.post("/infer")
async def infer_entity(request: Request):
    detection_data = await request.json()

    # Validate if there are entities to save and if the camera has been infered already
    if detection_data['entities'] is None or len(detection_data['entities']) == 0:
        return JSONResponse(status_code=400, content={"detail": "No entities provided"})
    observedCamera = await client.get(detection_data['entities'][0]['camera'])
    if observedCamera is None:
        return JSONResponse(status_code=404, content={"detail": "Camera not found"})
    if observedCamera['infered'].value:
        return JSONResponse(status_code=200, content={"detail": "Camera already infered"})

    # Get homography from calibrations
    camera_id = detection_data['camera_id']
    calibration_data = await client.get(f'urn:ngsi-ld:calibrations:{camera_id}')
    homography = calibration_data['homography'].value

    # Iterate over entities and save them in the context broker
    new_entities = []
    for entity_item in detection_data['entities']:
        entity_item['geo_coordinates'] = sample_homography(homography, entity_item['coordinates'])
        person_entity = build_person_entity(entity_item)
        new_entities.append(person_entity.to_dict())
        await client.upsert(person_entity)

    # Update camera video to infered
    observedCamera['infered'].value = True
    await client.update(observedCamera)

    return JSONResponse(status_code=201, content=jsonable_encoder(new_entities))


@app.post('/calibration/{camera_id}')
async def save_calibration(camera_id: str, request: Request):
    """Save source and target points for calibration"""
    data = await request.json()
    source = data['source_points']
    target = data['target_points']
    homography = compute_homography(source, target)
    camera = dict(id=camera_id, source_points=source, target_points=target, homography=homography)
    camera_entity = build_calibration_entity(camera)
    await client.upsert(camera_entity)
    return JSONResponse({}, 200)


@app.get('/calibration/{camera_id}')
async def get_calibration(camera_id: str):
    """Get the estimated sample's perspective transform"""
    camera_id = f'urn:ngsi-ld:calibrations:{camera_id}'
    has_calibration = await client.exists(camera_id)
    if not has_calibration:
        return { "source_points": [], "target_points": [], "homography": [] }
    calibration_info = await client.get(camera_id)
    return {
        'source_points': calibration_info['source_points'].value,
        'target_points': calibration_info['target_points'].value,
        'homography': calibration_info['homography'].value,
    }


@app.post('/test/calibration')
async def test_calibration(request: Request):
    """Test the estimated sample's perspective transform given source and target points"""
    data = await request.json()
    source = data['source_points']
    target = data['target_points']
    samples = data['sample_points']
    homography = compute_homography(source, target)
    estimate_point = sample_homography(homography, samples)
    return {"estimate_point": estimate_point}


@app.post('/sample/calibration')
async def sample_calibration(request: Request):
    """Calculate the estimated sample's perspective transform from a given camera calibration"""
    data = await request.json()
    camera_id = data['camera_id']
    camera_id = f'urn:ngsi-ld:calibrations:{camera_id}'
    samples = data['sample_points']
    has_calibration = await client.exists(camera_id)
    if not has_calibration:
        return JSONResponse(status_code=404, content={"detail": "Camera not found"})
    calibration_info = await client.get(camera_id)
    homography = calibration_info['homography']
    estimate_point = sample_homography(homography, samples)
    return {"estimate_point": estimate_point}


def compute_homography(source, target):
    """Calculate the homography from source to target using RANSAC."""
    assert len(source) >= MIN_NUM_POINTS and len(source) == len(target), f"Source and target require at least {MIN_NUM_POINTS} points each"
    source = np.array(source).astype(np.float32).reshape(-1, 1, 2)
    target = np.array(target).astype(np.float32).reshape(-1, 1, 2)
    homography_matrix, status = cv2.findHomography(source, target, cv2.RANSAC, 5.0)
    return homography_matrix.tolist()


def sample_homography(homography, samples):
    """Get the estimated sample's perspective transform"""
    homography_matrix = np.array(homography).astype(np.float32)
    sample_matrix = np.array(samples).astype(np.float32).reshape(-1, 1, 2)
    estimate_matrix = cv2.perspectiveTransform(sample_matrix, homography_matrix)
    estimate_matrix = estimate_matrix.reshape(-1, 2).tolist()
    return estimate_matrix


@app.get('/')
async def get_entities(before: int, after: int):
    """Get image entities"""
    before_date = iso8601.from_datetime(datetime.fromtimestamp(int(before) / 1000))
    after_date = iso8601.from_datetime(datetime.fromtimestamp(int(after) / 1000))
    people_entities = await client.query(type='personObserved', q=f'coordinates.observedAt>{after_date}&coordinates.observedAt<{before_date}')
    entity_dates = [
        # TODO: Change date format
        datetime.strptime(x['coordinates']['observedAt'], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%Y-%m-%d %H:%M')
        for x in people_entities
    ]
    entities = {x: entity_dates.count(x) for x in set(entity_dates)}
    entities = [{'taken_at': x, 'people_count': entities[x]} for x in entities]
    return {'processed_images': entities}


@app.get('/people/')
async def get_people_filter(before: int, after: int):
    """Get all of the people entities"""
    before_date = iso8601.from_datetime(datetime.fromtimestamp(int(before) / 1000))
    after_date = iso8601.from_datetime(datetime.fromtimestamp(int(after) / 1000))
    people_entities = await client.query(type='personObserved', q=f'coordinates.observedAt>{after_date}&coordinates.observedAt<{before_date}')
    get_coords = lambda entity: [
        dict(lat=coord[0], lon=coord[1], taken_at=timestamp)
        for coord, timestamp in zip(entity['geo_coordinates']['value'], entity['timestamps']['value'])
    ]
    geo_coordinates = list(chain(*[get_coords(x) for x in people_entities]))
    return {'points': geo_coordinates}


@app.get('/tooltip/')
async def get_tooltip_data(before: int, after: int):
    """Function to fetch data for the tooltip"""
    before_date = iso8601.from_datetime(datetime.fromtimestamp(int(before) / 1000))
    after_date = iso8601.from_datetime(datetime.fromtimestamp(int(after) / 1000))
    people_entities = await client.query(type='personObserved', q=f'coordinates.observedAt>{after_date}&coordinates.observedAt<{before_date}')
    activities_from_cam_id = [
        dict(
            id=int(x['camera']['object'].split(':')[3]),
            activity=x['activity']['value'],
            coords=x['geo_coordinates']['value']
        )
        for x in people_entities
    ]
    daydiff = get_date_count(after, before)

    activities = {}
    for item in activities_from_cam_id:
        key = item['id']
        if key not in activities:
            activities[key] = dict(**{x: 0 for x in ACTIVITIES}, count=0, daydiff=daydiff, lat=[], lon=[], label=f'Camera {key}')
        activities[key][item['activity']] += 1
        activities[key]['count'] += 1
        activities[key]['lat'].extend([x[0] for x in item['coords']])
        activities[key]['lon'].extend([x[1] for x in item['coords']])
    for key in activities:
        activities[key]['lat'] = sum(activities[key]['lat']) / len(activities[key]['lat'])
        activities[key]['lon'] = sum(activities[key]['lon']) / len(activities[key]['lon'])
    return list(activities.values())

@app.get('/coords/')
async def change_coords():
    """Function to correct inverted latitudes and longitudes"""
    db = get_database()
    coll = db.people
    ppl = list(coll.find({}))
    for p in ppl:
        if p['lat'] < 0:
            coll.update_one(
                {'_id': ObjectId(p['_id'])}, 
                {"$set": {'lat': p['lon'], 'lon': p['lat']}})
    

@app.get('/current_people')
async def get_current_people():
    num_entities = await client.count(type='personObserved')
    return {'count': num_entities}

@app.get('/modify_data')
async def modify_data():
    """Generic function to modify data in the database from the endpoint"""
    db = get_database()
    data = db.processed_images.find({}, {'_id': False})
    db.processed_images.update({}) # Change method parameters to update data
    print(data)
    return list(data)

@app.get('/activities')
async def get_activities(before: str, after: str):
    """Get all activities within the selected timestamps"""
    before_date = iso8601.from_datetime(datetime.fromtimestamp(int(before) / 1000))
    after_date = iso8601.from_datetime(datetime.fromtimestamp(int(after) / 1000))
    people_entities = await client.query(type='personObserved', q=f'coordinates.observedAt>{after_date}&coordinates.observedAt<{before_date}')
    activities = set([
        x['activity']['value'] for x in people_entities
    ])
    return {'activities': list(activities)}

@app.get('/activities_by_date')
async def get_activities_by_date(before: str, after: str):
    """Get all activities within the selected timestamps and group them by day"""
    before_date = iso8601.from_datetime(datetime.strptime(before, '%Y-%m-%d'))
    after_date = iso8601.from_datetime(datetime.strptime(after, '%Y-%m-%d'))
    people_entities = await client.query(type='personObserved', q=f'coordinates.observedAt>{after_date}&coordinates.observedAt<{before_date}')
    activities = [
        dict(
            date=datetime.strptime(x['coordinates']['observedAt'], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%Y-%m-%d %H:%M:%S'),
            activity=x['activity']['value']
        )
        for x in people_entities
    ]
    activities_by_day = {}
    for activity in activities:
        if activity['activity'] not in activities_by_day:
            activities_by_day[activity['activity']] = {}
        if activity['date'] not in activities_by_day[activity['activity']]:
            activities_by_day[activity['activity']][activity['date']] = 0
        activities_by_day[activity['activity']][activity['date']] += 1
    activities_by_day = {
        activity: sorted([
            dict(date=date, count=count)
            for date, count in activities_by_day[activity].items()
        ], key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'))
        for activity in activities_by_day
    }
    return activities_by_day

@app.get('/top_activities')
async def get_top_activities(before: str, after: str):
    """Get all activities and sort them by trend"""
    before_date = iso8601.from_datetime(datetime.strptime(before, '%Y-%m-%d'))
    after_date = iso8601.from_datetime(datetime.strptime(after, '%Y-%m-%d'))
    people_entities = await client.query(type='personObserved', q=f'coordinates.observedAt>{after_date}&coordinates.observedAt<{before_date}')
    activities = {}
    for entity in people_entities:
        activity = entity['activity']['value']
        if activity not in activities:
            activities[activity] = 0
        activities[activity] += 1
    return activities

@app.get('/insert_activities/')
async def activities_create():
    insert_activities()
    delete_duplicate_activities()
    return JSONResponse({}, status_code=200)

@app.get('/insert_people/')
async def people_create():
    insert_people()
    return JSONResponse({}, status_code=200)

@app.get('/insert_processed_images/')
async def processed_images_create():
    insert_processed_images()
    return JSONResponse({}, status_code=200)

@app.get('/health')
async def get_backend_health():
    return JSONResponse({}, status_code=200)
