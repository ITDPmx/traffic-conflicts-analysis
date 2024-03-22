from threading import Thread
import cv2
import os
import datetime
import ffmpegcv
import time
import imutils
import argparse
#Local imports
from Generic.Global.Borg import Borg
from System.App.Uploader.Uploader import Uploader
from System.App.Scrambling.Scrambling import Scrambling
import numpy as np
#Director class
class RTSPRecorder(Borg):

    #Contextual generic objects
    __ctx = None

    #Configuration data
    __config = None

    def __init__(self, 
                 camera: str='camera1', 
                 folder: str='',
                 codec: str='h264',
                 width: int=None,
                 height: int=None,
                 fps: int=None,
                 scrambling: bool=False,
                 verbose: bool=False):

        """
        Class builder, all the contextual configurations are charged from the base class (borg pattern) in a shared state
        Returns:
            [None]: None
        """
        #Setting contextual generic objects
        super().__init__()        
        src = self.ctx['__obj']['__config'].get('rtsp')[camera]
        self.ctx_rtsp = { "camera": camera,
                          "capture": cv2.VideoCapture ( src, cv2.CAP_FFMPEG ),
                          "output_video": None,
                          "folder": folder,
                          "fps": fps,
                          "width": width,
                          "height": height,
                          "codec": codec,
                          "verbose": verbose,
                          "scrambling": scrambling
                        }
        self.writing_video = False
        self.active = True
        self.recording = False
        self.mutithreadingRead()
        self.uploader = Uploader()

        #Bye
        return None
    
    def mutithreadingRead(self):
        """
        Multithreading reading of RTSP Streming of the IP cameras. 
        Args:
            [None]: None
                               
        Returns:
            [None]: None
        """
        self.ctx['__obj']['__log'].setLog('Starting multithreading')
        self.readStatus, frame = self.ctx_rtsp["capture"].read()
        if not self.readStatus:
            self.ctx['__obj']['__log'].setLog( "[ERROR] Failed to read from video stream")
            return
        #resize
        self.frame = self.resize(frame)
        #Start the thread to read frames from the video stream
        self.cameraThread = Thread(target=self.update, args=())
        self.cameraThread.daemon = True
        self.readStatus = False
        self.cameraThread.start()
        #Bye
        return None

    def resize(self,frame):
        #Resize frame to desired width/height
        if self.ctx_rtsp["width"] is not None or self.ctx_rtsp["height"] is not None:
            #If one of the dimensions is None, resize while maintaining aspect ratio
            rframe = imutils.resize(frame, 
                                        width=self.ctx_rtsp["width"], 
                                        height=self.ctx_rtsp["height"])
        else:
            rframe = frame
        
        return rframe

    def update(self):
        #Setting initial time mark for recording procedure
        timemark = time.perf_counter()
        #Starting log
        self.ctx['__obj']['__log'].setLog( f"[INFO] Starting the capturing process in the {self.ctx_rtsp['camera']}" )
        # Read the next frame from the stream in a different thread
        time_inactivity = 0
        while self.active:
            if self.ctx_rtsp["capture"].isOpened():
                try:
                    (self.readStatus, frame) = self.ctx_rtsp["capture"].read()
                    #resize
                    self.frame = self.resize(frame)
                    if self.frame is None or not self.readStatus:
                        pass
                    if self.recording:
                        self.writing_video = True
                        self.ctx_rtsp['output_video'].write(self.frame)
                        self.writing_video = False
                    # Every one minute, print the camera is ok
                    if time.perf_counter() - timemark > 60:
                        self.ctx['__obj']['__log'].setLog( f"[INFO] {self.ctx_rtsp['camera']} is capturing correcly" )
                        timemark = time.perf_counter()
                except Exception as e:
                    # one frame was missed, but the stream is probably still alive
                    time_inactivity += 0.5
                    time.sleep(0.5)
                    if time_inactivity > 5:
                        self.ctx['__obj']['__log'].setLog( f"[ERROR] {self.ctx_rtsp['camera']} is not capturing correcly, retrying..." )
                        # close and reopen the stream
                        self.ctx_rtsp["capture"].release()
                        self.ctx_rtsp["capture"] = cv2.VideoCapture ( self.ctx_rtsp["camera"], cv2.CAP_FFMPEG )
                        time_inactivity = 0
                    pass
            else:
                # self.ctx['__obj']['__log'].setLog( f"[ERROR] {self.ctx_rtsp['camera']} is not capturing correcly, retrying..." )
                # send black image to stop any recording
                self.frame = np.zeros((self.ctx_rtsp["height"], self.ctx_rtsp["width"], 3), np.uint8)
                time.sleep(1)
                # close and reopen the stream
                self.ctx_rtsp["capture"].release()
                self.ctx_rtsp["capture"] = cv2.VideoCapture ( self.ctx_rtsp["camera"], cv2.CAP_FFMPEG )
                time_inactivity = 0
        if self.ctx_rtsp['verbose']:
            self.ctx['__obj']['__log'].setLog('[INFO] Finished reading frames cleanly in [' + str( time.perf_counter() - timemark ) + '] sec.')
    
    def get_frame(self):
        # Return the most recent frame (a numpy array) from the video stream
        frame = self.frame.copy()
        return frame

    def show_frame(self):
        # Display frames in main program
        if self.readStatus:
            cv2.imshow('frame', self.frame)
        
        # Press Q on keyboard to stop frame show
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
    
    def show_video(self):
        # wait at most 5 seconds for self.readStatus to be True, dont use time.sleep
        startTime = time.time()
        while not self.readStatus:
            if time.time() - startTime > 5:
                self.ctx['__obj']['__log'].setLog("[ERROR] Failed to show video stream")
                return
        self.videoThread = Thread(target=self.show_video_thread, args=())
        self.videoThread.daemon = True
        self.videoThread.start()

    def show_video_thread(self):
        # Display video from the stream
        if self.verbose:
            self.ctx['__obj']['__log'].setLog("[INFO] Showing video...")
        while self.readStatus and self.active:
            cv2.imshow('frame', self.frame)
            # Press Q on keyboard to stop video show
            key = cv2.waitKey(1)
            if key == ord('q'):
                self.capture.release()
                cv2.destroyAllWindows()
                break

    def startRecording(self):
        
        #Build directory path and filename
        GP = self.ctx['__obj']['__global_procedures']
        file = GP.getTodayString(mask = "%Y_%m_%d-%I_%M_%S_%p") + '.mp4'
        dir = GP.createDirectory(dir = ['records', 
                                        GP.getTodayString("%Y_%m_%d"), 
                                        self.ctx_rtsp['camera']
                                       ],
                                 base = self.ctx_rtsp['folder']
                                )
        self.uploader.createDir(self.ctx_rtsp['camera'])  
        self.filename = dir + file
        #Build videowriter object
        if self.ctx_rtsp['fps'] is None:
            self.ctx_rtsp['fps'] = self.ctx_rtsp['capture'].get(cv2.CAP_PROP_FPS)
            self.ctx_rtsp['output_video'] = ffmpegcv.VideoWriter(self.filename,
                                                     self.ctx_rtsp['codec'],
                                                     self.ctx_rtsp['fps']
                                                     )
        else:
            self.ctx_rtsp['output_video'] = ffmpegcv.VideoWriter(self.filename,
                                                     self.ctx_rtsp['codec'],
                                                     self.ctx_rtsp['fps'])
        self.recording = True
    
    def stopRecording(self):
        # Stop recording frames
        self.recording = False
        while self.writing_video:
            pass
        self.ctx_rtsp['output_video'].release()
        if self.ctx_rtsp['scrambling']:
            encryptThread = Thread(target=self.encryptFile, args=(self.filename,))
            encryptThread.daemon = True
            encryptThread.start()
    
    def encryptFile(self, filename):
        self.ctx['__obj']['__log'].setLog('Encrypting records of {}'.format(self.ctx_rtsp['camera']))
        Scrambling.encryptFile(filename)
        self.ctx['__obj']['__log'].setLog(f'Encripted records of {self.ctx_rtsp["camera"]} as {filename}.enc')

    
    def release(self):
        # Release the video capture and output
        self.active = False
        if self.recording:
            self.stopRecording()
        self.ctx_rtsp['capture'].release()
        cv2.destroyAllWindows()
        self.ctx['__obj']['__log'].setLog("[INFO] Finished releasing video capture and output")


