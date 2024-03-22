# Uses rtspRecorder to record the video when movement is detected
# Movement is detected using absdiff and thresholding
# Uses ROI to only detect movement in a specific area

import threading
import cv2
import os
import datetime
import ffmpegcv
import time
import imutils
import argparse
import numpy as np
#Local imports
from Generic.Global.Borg import Borg
from System.App.Uploader.Uploader import Uploader
from System.App.RTSPRecorder.RTSPRecorder import RTSPRecorder


class MovementDetector(Borg):

    #Contextual generic objects
    __ctx = None

    #Configuration data
    __config = None

    def __init__(self,
                 camera: str='camera1',
                 model=None,
                 ROI: str=None, 
                 treshold: float=0.002, 
                 time_between_detections: int=1, 
                 clip_duration: int=5, 
                 folder: str='', 
                 codec: str='h264', 
                 width: int=None, 
                 height: int=None, 
                 src_fps: int=None, 
                 scrambling: bool=False,
                 verbose: bool=False, 
                 visualize: bool=False) -> None:
        
        super().__init__()        
        src = self.ctx['__obj']['__config'].get('rtsp')[camera]

        self.ctx_mov = {  "src": src,
                            "src_name": camera,
                            "model": model,
                            "ROI": ROI,
                            "treshold": treshold,
                            "time_between_detections": time_between_detections,
                            "clip_duration": clip_duration,
                            "folder": folder,
                            "codec": codec,
                            "width": width,
                            "height": height,
                            "src_fps": src_fps,
                            "verbose": verbose,
                            "visualize": visualize
                        }
        # CONSTANTS        

        self.TIME_BETWEEN_DETECTIONS = time_between_detections # seconds
        self.CLIP_MIN_DURATION = clip_duration # seconds
        self.BLUR_INTENSITY = 15 # pixels
        self.DIFFERENCE_THRESHOLD = 0.003 # As a percentage of image
        self.PIXEL_TRESHOLD = 30 # Treshold to be considered a different pixel

        # recording states
        self.RECORDING = 1
        self.NOT_RECORDING = 0
        self.curr_state = self.NOT_RECORDING
        self.recording_start_time = 0

        self.src = src
        src_name = camera
        if src_name is None:
            self.src_name = str(src)
        else:
            self.src_name = src_name
        self.roi_src = ROI
        self.treshold = treshold
        self.folder = folder
        self.codec = codec
        self.width = width
        self.height = height
        self.src_fps = src_fps
        self.verbose = verbose
        self.visualize = visualize
        self.model = model

        # start RTSVideoRecorder
        self.recorder = RTSPRecorder(camera=camera, folder=folder, codec=codec, width=width, height=height, fps=src_fps, scrambling=scrambling, verbose=verbose)
        # get first frame
        frame = self.recorder.get_frame()

        # get ROI mask
        if self.roi_src is not None:
            self.roi_mask = self.get_ROI_mask(self.roi_src, frame)
        else:
            self.roi_mask = np.ones(frame.shape, dtype=np.uint8)*255

        self.run_active = False
        self.ctx['__obj']['__log'].setLog(f"[INFO] Initialized movement detection object for {self.src_name}")

    def get_ROI_mask(self, roi_src, frame):
        # load ROI either from disk or directly the numpu array
        if roi_src.endswith('.npy'):
            roi = np.load(roi_src)
        else:
            roi = roi_src
        # convert from percentages to pixels
        roi[:,0] = roi[:,0]*frame.shape[1]
        roi[:,1] = roi[:,1]*frame.shape[0]
        # convert ROI points to mask
        mask = np.zeros(frame.shape, dtype=np.uint8)
        cv2.fillPoly(mask, np.int32([roi]), (255,255,255))
        return mask

    def start(self):
        self.run_active = True
        # run detection in a separate thread
        self.thread = threading.Thread(target=self.run)
        self.ctx['__obj']['__log'].setLog(f"[INFO] Starting movement detection for {self.src_name}")
        self.thread.start()
    
    def start_inference(self):
        if self.ctx_mov["model"] is None:
            self.ctx['__obj']['__log'].setLog("[ERROR] No model specified")
            return
        self.run_active = True
        # run detection in a separate thread
        self.thread = threading.Thread(target=self.run_inference)
        self.ctx['__obj']['__log'].setLog(f"[INFO] Starting human detection for {self.src_name}")
        self.thread.start()


    def run(self):
        # get first frame
        prev_frame = self.recorder.get_frame()
        prev_frame = cv2.bitwise_and(prev_frame, self.roi_mask)
        prev_frame = cv2.GaussianBlur(prev_frame, (self.BLUR_INTENSITY, self.BLUR_INTENSITY), 0)
        last_frame_time = time.time()
        while self.run_active:
            # update according to TIME_BETWEEN_DETECTIONS
            if time.time() - last_frame_time < self.TIME_BETWEEN_DETECTIONS:
                continue
            last_frame_time = time.time()
            # use getFrame to get a frame from the video
            frame = self.recorder.get_frame()
            if frame is None:
                break
            # apply mask to frame
            frame = cv2.bitwise_and(frame, self.roi_mask)
            # blur
            frame = cv2.GaussianBlur(frame, (self.BLUR_INTENSITY, self.BLUR_INTENSITY), 0)
            # calculate difference between frames
            diff = cv2.absdiff(frame, prev_frame)
            diff[diff < self.PIXEL_TRESHOLD] = 0
            # get difference as a number between 0 and 1
            numdiff = diff.astype(np.int32)
            percent_diff = np.sum(numdiff)/(numdiff.shape[0]*numdiff.shape[1]*255)
            if self.verbose:
                self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Percent diff: {round(percent_diff,3)}")

            # if difference is greater than threshold, save video
            if percent_diff > self.DIFFERENCE_THRESHOLD:
                if self.verbose:
                    self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Movement detected")
                # start recording
                if self.curr_state == self.NOT_RECORDING:
                    self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Starting recording")
                    self.recorder.startRecording()
                    self.curr_state = self.RECORDING
                # restore recording start time, so that it doesn't stop recording
                recording_start_time = time.time()
            # if recording, and remaining recording time is less than 0, stop recording
            elif self.curr_state == self.RECORDING:
                if self.verbose:
                    self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Movement not detected, remaining recording time: {round(self.CLIP_MIN_DURATION - (time.time() - recording_start_time),2)}")
                if time.time() - recording_start_time > self.CLIP_MIN_DURATION:
                    self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Stopping recording")
                    self.recorder.stopRecording()
                    self.curr_state = self.NOT_RECORDING
            
            prev_frame = frame
            
            #show frame
            if self.visualize:
                # show the difference frame
                gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                # blur
                gray = cv2.GaussianBlur(gray, (1, 1), 0)
                # treshold gray image
                thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)[1]
                dilated = cv2.dilate(thresh, None, iterations=2)
                # show the difference frame
                cv2.imshow(f'diff : {self.src_name}', dilated)

                # show the original frame
                cv2.imshow(f'frame : {self.src_name}', frame)
                # Press Q on keyboard to stop video show
                key = cv2.waitKey(1)
                if key == ord('q'):
                    self.visualize = False
                    cv2.destroyAllWindows()

    def run_inference(self):
        def generate_boxes_confidences_classids_v8(outs, threshold):
            boxes = []
            confidences = []
            classids = []

            for out in outs:
                    for box in out.boxes:
                        x1, y1, x2, y2 = [round(x) for x in box.xyxy[0].tolist()]
                        class_id = box.cls[0].item()
                        prob = round(box.conf[0].item(), 2)
                        if prob > threshold:
                            # Append to list
                            boxes.append([x1, y1, x2-x1, y2-y1])
                            confidences.append(float(prob))
                            classids.append(class_id)
        
            return boxes, confidences, classids
        # get first frame
        prev_frame = self.recorder.get_frame()
        last_frame_time = time.time()

        predictions_num = 0
        prediction_time_accum = 0
        prev_time_prediction_time = datetime.datetime.now()

        while self.run_active:
            # update according to TIME_BETWEEN_DETECTIONS
            if time.time() - last_frame_time < self.TIME_BETWEEN_DETECTIONS:
                continue
            last_frame_time = time.time()
            # use getFrame to get a frame from the video
            frame = self.recorder.get_frame()
            if frame is None:
                pass
            # apply mask to frame
            prevtime = time.time()
            detections = self.model.predict(source=frame, verbose=False)
            # Get boxes, confidences and classids
            boxes, confidences, classids = generate_boxes_confidences_classids_v8(detections, 0.4)
            #self.ctx['__obj']['__log'].setLog(f"Prediction done in {time.time() - prevtime} seconds")
            # accumulate time of predictions, to print average
            prediction_time_accum += time.time() - prevtime
            # every minute, print average prediction time

            
            # if detectinons are found and at least one is a person
            if len(boxes) > 0 and 0 in classids:
                # if difference is greater than threshold, save video
                for box in boxes:
                    x, y, w, h = box
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    # only if classid is 0 (person)
                    if classids[boxes.index(box)] == 0:
                        if self.verbose:
                            #self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Person detected")
                            pass
                        # start recording
                        if self.curr_state == self.NOT_RECORDING:
                            self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Starting recording")
                            self.recorder.startRecording()
                            self.curr_state = self.RECORDING
                        # restore recording start time, so that it doesn't stop recording
                        recording_start_time = time.time()
            # if recording, and remaining recording time is less than 0, stop recording
            elif self.curr_state == self.RECORDING:
                if self.verbose:
                    self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Person not detected, remaining recording time: {round(self.CLIP_MIN_DURATION - (time.time() - recording_start_time),2)}")
                if time.time() - recording_start_time > self.CLIP_MIN_DURATION:
                    self.ctx['__obj']['__log'].setLog(f"[INFO] {self.src_name} : Stopping recording")
                    self.recorder.stopRecording()
                    self.curr_state = self.NOT_RECORDING

            #show frame
            if self.visualize:
                
                # show the original frame
                cv2.imshow(f'frame : {self.src_name}', frame)
                # Press Q on keyboard to stop video show
                key = cv2.waitKey(1)
                if key == ord('q'):
                    self.visualize = False
                    cv2.destroyAllWindows()
    def stop(self):
        self.ctx['__obj']['__log'].setLog("[INFO] Releasing thread")
        self.run_active = False
        if (self.curr_state == self.RECORDING):
            self.recorder.stopRecording()
        self.recorder.release()
        cv2.destroyAllWindows()
        self.ctx['__obj']['__log'].setLog("[INFO] Finished releasing video capture and output")
        pass

def yolov8_warmup(self, model, repetitions=1, verbose=False):
        # Warmup model
        # create an empty frame to warmup the model
        warmupFrame = np.zeros((360, 640, 3), dtype=np.uint8)
        for i in range(repetitions):
            model.predict(source=warmupFrame, verbose=verbose)