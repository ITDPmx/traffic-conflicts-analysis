import cv2
import numpy as np
import flow_vis
from ultralytics import YOLO
from typing import List, Tuple, Optional
import torch
import json
import pandas as pd
#Local imports
from Generic.Global.Borg import Borg
from System.App.WidthHeightModel.WidthHeightModel import WidthHeightModel

#AWS
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

class OBBDetector (Borg):

    #Contextual generic objects
    __ctx = None

    #Configuration data
    __config = None

    #-----------------------------------------------------------------------------------------------------------------------------

    def __init__(self, video_path: str, id_video, model_path: str, model_obb_path: str, model_WHE_path: str) -> None:
        """
        Class builder, all the contextual configurations are charged from the base class (borg pattern) in a shared state
        Returns:
            [None]: None
        """
        #Setting contextual generic objects
        super().__init__()
        self.id_video = id_video
        self.GP = self.ctx['__obj']['__global_procedures']
        self.video = cv2.VideoCapture(video_path)
        self.model = YOLO(model_path)
        self.model_obb = YOLO(model_obb_path)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.data = []  # List to store data for DataFrame
        self.model_WHE = WidthHeightModel()
        self.model_WHE.load_state_dict(torch.load(model_WHE_path))
        self.model_WHE.eval()
        self.class_mapping = {0: "car", 1: "truck", 2: "van", 3: "bus", 4: "pedestrian", 5: "cyclist", 6: "tricyclist", 7: "motorcyclist"}
        self.labels_map = {0: 4, 1: 5, 2: 0, 3: 7, 5: 3, 7: 1}
        self.labels_map_coco = {0: "pedestrian", 1: "cyclist", 2: "car", 3: "motorcyclist", 5: "bus", 7: "truck"}
        load_dotenv()
        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") 
        self.AWS_BUCKET_NAME = 'tca-itdp-tec-prod'
        AWS_REGION = 'us-east-1'

        self.S3_CLIENT = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION )       
    #-----------------------------------------------------------------------------------------------------------------------------
    def process_video(self):
        frame_ix = 0
        ret, frame = self.video.read()
        for _ in range(self.frames - 1):
            ret, frame_sig = self.video.read()
            if not ret:
                continue

            act = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sig = cv2.cvtColor(frame_sig, cv2.COLOR_BGR2GRAY)
            results_2d = self.model.track(frame, persist=True, conf=0.3, iou=0.7, agnostic_nms=True, verbose=False)
            results_obb = self.model_obb.track(frame, persist=True, conf=0.3, iou=0.7, agnostic_nms=True, verbose=False)
            timestamp = self.video.get(cv2.CAP_PROP_POS_MSEC)
            self.process_frame(frame, frame_sig, act, sig, results_2d, results_obb, timestamp, frame_ix)
            frame_ix += 1
            frame = frame_sig.copy()
            if frame_ix % (self.frames/50) == 0: #each 2% progress
                response = requests.post('https://tca.mexico.itdp.org/api/progress', json={"id": self.id_video, "progress": (frame_ix/self.frames)*90 })
        
        self.video.release()
        # self.out.release()
        return pd.DataFrame(self.data)

    #-----------------------------------------------------------------------------------------------------------------------------

    def process_frame(self, frame: np.ndarray, frame_sig: np.ndarray, act: np.ndarray, sig: np.ndarray, results_2d, results_obb, timestamp: float, frame_ix: int) -> None:
        boxes_2d = results_2d[0].boxes
        boxes_obb = results_obb[0].obb
        masks_2d, flow, flow_mag_color = self.get_masks_and_flow(act, sig, results_2d)
        track_ids = self.get_track_ids(results_2d)
        boxes, scores = self.get_boxes_and_scores(boxes_2d)

        if track_ids:
            filtered_boxes, indices = self.GP.apply_nms(boxes, scores, iou_threshold=0.7)
            filtered_track_ids = [track_ids[i] for i in indices]
            filtered_masks = [masks_2d[i] for i in indices]
            filtered_boxes_2d = [boxes_2d[i] for i in indices]
            self.extract_trajs_atts( filtered_boxes, filtered_track_ids, filtered_masks, filtered_boxes_2d, boxes_obb, flow_mag_color, flow, self.fps, timestamp, frame_ix)

    def uploadFile(self, file, filename):
        try:
            with open(file, 'rb') as file:
                self.S3_CLIENT.upload_fileobj(file, self.AWS_BUCKET_NAME, filename)
            print("File uploaded successfully to bucket with key")
        except Exception as e:
            print("An error occurred")

    @staticmethod
    def get_masks_and_flow(act: np.ndarray, sig: np.ndarray, results_2d) -> Tuple[List[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        try:
            masks_2d = results_2d[0].masks.xy
            flow = cv2.calcOpticalFlowFarneback(act, sig, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            flow_mag_color = flow_vis.flow_to_color(flow, convert_to_bgr=False)
        except Exception:
            masks_2d, flow, flow_mag_color = [], None, None
        return masks_2d, flow, flow_mag_color

    @staticmethod
    def get_track_ids(results_2d) -> List[int]:
        try:
            return results_2d[0].boxes.id.int().cpu().tolist()
        except Exception:
            return []

    @staticmethod
    def get_boxes_and_scores(boxes_2d) -> Tuple[List[List[int]], List[float]]:
        boxes, scores = [], []
        for det_2d in boxes_2d:
            box = [int(x) for x in det_2d.xyxy[0]]
            score = float(det_2d.conf)
            boxes.append(box)
            scores.append(score)
        return boxes, scores
    #-----------------------------------------------------------------------------------------------------------------------------
    def extract_trajs_atts(self, filtered_boxes, filtered_track_ids, filtered_masks, filtered_boxes_2d, boxes_obb, flow_mag_color, flow, fps, timestamp, frame_ix):
        iou_threshold = 0.3
        for i in range(len(filtered_track_ids)):
            box_2d = self.GP.convert_xyxy_to_xyxyxyxy(filtered_boxes[i])
            best_iou, best_box_obb = self.find_best_iou_box(box_2d, boxes_obb, iou_threshold)

            if best_iou > iou_threshold:
                label, xywhr = self.get_obb_box_and_label(best_box_obb)
                direction_vector = self.GP.get_dir_vect(filtered_masks[i], flow)
                obb_flag = True
                conf = float(best_box_obb.conf)
            else:
                label, xywhr, direction_vector = self.get_2d_box_and_label(filtered_masks[i], flow, int(filtered_boxes_2d[i].cls))
                obb_flag = False
                conf = float(filtered_boxes_2d[i].conf)

            # Collect data for DataFrame
            self.data.append({
                'id': filtered_track_ids[i],
                'frame_ix': frame_ix,
                'timestamp': timestamp,
                'x': xywhr[0],
                'y': xywhr[1],
                'w': xywhr[2],
                'h': xywhr[3],
                'dir_vect': json.dumps(direction_vector.tolist()),
                'label': label,
                'fps': fps,
                'mask': json.dumps(filtered_masks[i].tolist()),
                'obb_flag': obb_flag,
                'conf': conf
            })



    #-----------------------------------------------------------------------------------------------------------------------------
    def find_best_iou_box(self, box_2d, boxes_obb, iou_threshold):
        best_iou = 0
        best_box_obb = None
        for det_obb in boxes_obb:
            corners = det_obb.xyxyxyxy.cpu().numpy().tolist()[0]
            box_obb = [(int(corner[0]), int(corner[1])) for corner in corners]
            iou = self.GP.calculate_iou(box_2d, box_obb)
            if iou > best_iou:
                best_iou = iou
                best_box_obb = det_obb
        return best_iou, best_box_obb
    
    #-----------------------------------------------------------------------------------------------------------------------------

    def get_obb_box_and_label(self, best_box_obb):
        label = self.class_mapping.get(int(best_box_obb.cls), "misc")
        xywhr = best_box_obb.xywhr.cpu().numpy().tolist()[0]
        xywhr[2], xywhr[3] = xywhr[3], xywhr[2]  # Swap w and h
        return label, xywhr


    #-----------------------------------------------------------------------------------------------------------------------------

    def get_2d_box_and_label(self, mask, flow, cls):
        centroid = self.GP.get_centroid(mask)
        direction_vector = self.GP.get_dir_vect(mask, flow)
        direction_angle = np.arctan2(direction_vector[1], direction_vector[0])
        input_vector = [centroid[0], centroid[1], direction_angle, self.labels_map[cls]]
        input_tensor = torch.tensor([input_vector], dtype=torch.float32)

        with torch.no_grad():
            output = self.model_WHE(input_tensor)
            predicted_width_height = output.numpy()[0]

        xywhr = input_vector[:2] + list(predicted_width_height) + [input_vector[2]]
        label = self.labels_map_coco[cls]
        return label, xywhr, direction_vector


if __name__ == "__main__":
    video_path = "181653_cam3_bev.mp4"
    model_path = "yolov9e-seg.pt"
    model_obb_path = "runs/obb/train9/weights/best.pt"
    model_WHE_path = 'best_width_height_estimator.pth'
    processor = OBBDetector(video_path, model_path, model_obb_path, model_WHE_path)
    processor.process_video()