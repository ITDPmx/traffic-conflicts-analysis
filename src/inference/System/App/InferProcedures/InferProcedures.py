import boto3
from glob import glob
import os
from ultralytics import YOLO
import asyncio
import requests
import random
import json
from datetime import datetime
import cv2
import numpy as np
from datetime import datetime, timedelta
#Local imports
from Generic.Global.Borg import Borg
from System.App.Scrambling.Scrambling import Scrambling


ACTIVITIES = ['running', 'reading', 'playing', 'walking']
DATE_FORMAT_S3 = '%Y_%m_%d-%I_%M_%S_%p'

def bbox_to_point(bbox):
  return [(bbox[0, 0] + bbox[1, 0]) / 2, bbox[1, 1]]


def sample_homography(homography, samples):
  """Get the estimated sample's perspective transform"""
  homography_matrix = np.array(homography).astype(np.float32)
  sample_matrix = np.array(samples).astype(np.float32).reshape(-1, 1, 2)
  estimate_matrix = cv2.perspectiveTransform(sample_matrix, homography_matrix)
  estimate_matrix = estimate_matrix.reshape(-1, 2).tolist()
  return estimate_matrix


#Procedures class

class InferProcedures(Borg):

    #Contextual generic objects
    __ctx = None

    #Configuration data
    __config = None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self) -> None:
        """
        Class builder, all the contextual configurations are charged from the base class (borg pattern) in a shared state
        Returns:
            [None]: None
        """
        #Setting contextual generic objects
        super().__init__()
        self.scrambler = Scrambling()
        self.s3_client = boto3.client('s3',
                                      aws_access_key_id = self.ctx['__obj']['__config'].get('aws')['access_key_id'],
                                      aws_secret_access_key = self.ctx['__obj']['__config'].get('aws')['secret_access_key']
                                     )
        #Bye
        return None
    #---------------------------------------------------------------------------------------------------------------------------------
    async def create_person_entities(self, cameras : list) -> list:
        """
        This method estimate a list of cameras entities and construct persons entities
        Args:
            list
        Returns:
            entities [list]
        """
        entities = []
        for camera in cameras:
            # Download the video and decrypt
            filevideo = self.download_video(camera['root']['bucket']['value'], camera['root']['file']['value'])
            # TODO: Do video decryption
            self.scrambler.decryptFile(filevideo)
            decryptedF = '.'.join(filevideo.split('.')[:-1])
            entities.append( self.infer(camera, decryptedF))
            # Update camera video to infered
            """
            camera['root']['infered']['value'] = True
            response = requests.post("http://127.0.0.1:8000/update", 
                                headers={'Content-Type':'application/json'},
                                data = json.dumps(camera))
            """
            os.remove(filevideo)
            os.remove(decryptedF)
        return entities
    #----------------------------------------------------------------------------------------------------------------   
    def download_video(self, bucket:str, file:str) -> str:
        """
        This method download a file video given a 
        bucket and object file path
        """

        file_name = file.split('/')[-1]
        os.makedirs('videos', exist_ok=True)
        new_path = f'videos/{file_name}'
        self.s3_client.download_file(bucket, file, new_path)
        return new_path
   #----------------------------------------------------------------------------------------------------------------
    def track_video(self, filevideo: str, model, time) -> dict:
        """
        This method run a tracker from ultralytics given a detector model and
        a video.
        Args:
            filevideo[str]: path to the video to track
            model: model of the detector that the tracker will use
            time: timestamp from the camera entity record
        Returns: 
            [dict]: a dictionary with person entities detected from the video
        """

        print(filevideo)
        video = cv2.VideoCapture(filevideo)
        frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        entities = {}
        for i_frame in range(frames):
            ret, frame = video.read()
            if not ret:
                continue
            # Track all objects in the frame
            results = model.track(source=frame, persist=True, classes=0, show=True)
            names = results[0].names
            boxes = results[0].boxes
            if not boxes.is_track:
                continue
            # Get the timestamp of the frame
            seconds = i_frame / video.get(cv2.CAP_PROP_FPS)
            timestamp = datetime.timestamp(time + timedelta(seconds=seconds))
            # Iterate over all detected objects
            for i, id in enumerate(boxes.id.int().tolist()):
                if id not in entities:
                    entities[id] = dict(classes=[], bboxes=[], coordinates=[], timestamps=[])
            _class = names[boxes.cls[i].int().tolist()]
            bbox = boxes.xyxy[i].numpy().astype(float).reshape((2, 2))
            # Get the coordinates of the bbox
            coord = bbox_to_point(bbox)
            # TODO: Fix weirdness with homography and coordinates
            # Explaination: The homography is saving the calibration info as [lat, lon] and therefore we need to adhere to the convention by swapping the coordinates.
            # bbox xyxy -> point coord [x, y] -> [lat, lon]
            coord = [1 - (coord[1] / height), coord[0] / width]
            entities[id]['classes'].append(_class)
            entities[id]['bboxes'].append(bbox)
            entities[id]['coordinates'].append(coord)
            entities[id]['timestamps'].append(timestamp)
        # TODO: Infer activity instead of assigning a random activity
        random_activity = ACTIVITIES[int(random.random() * len(ACTIVITIES))]
        # Get the most common class for each entity
        entities = {
            k: dict(
                **v,
                _class=max(v['classes'], key=v['classes'].count),
                activity=random_activity
            )
            for k, v in entities.items()
                   }
        return entities

    #---------------------------------------------------------------------------------------------------------------------------------
    def infer(self, camera: dict, filevideo: str) -> list:
        """
        This method build the person entity from the camera entity
        and map to real coordinates using the homography matrix

        Args:
            camera[dict]: the camera entity to be infered
            filevideo[str]: filevideo to be infered
        Returns:
            [list]: a list with the persons entities detected from the video
        """
 
        homography = requests.post("http://127.0.0.1:8000/homography", 
                                 headers={'Content-Type':'application/json'},
                                 data = json.dumps(camera)).json()
        
        time = datetime.fromtimestamp(camera['root']['timestamp']['value'])

        model = YOLO('yolov8l.pt')
        #model = YOLO('yolov8l-pose.pt')

        entities = self.track_video(filevideo, model, time)
        entities = [dict(id=k, coordinates=x['coordinates'], timestamps=x['timestamps'], activity=x['activity'], camera=camera['root']['id'])
                    for k, x in entities.items()
                    ]
        # Iterate over entities and save them in the context broker
        
        new_entities = []
        for entity in entities:
            entity['geo_coordinates'] = sample_homography(homography, entity['coordinates'])
            person_entity = requests.post("http://127.0.0.1:8000/create_person", 
                                 headers={'Content-Type':'application/json'},
                                 data = json.dumps(entity)).json()
            new_entities.append(person_entity)
        return new_entities
