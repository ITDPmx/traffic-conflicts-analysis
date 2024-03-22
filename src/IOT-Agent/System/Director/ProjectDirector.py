import datetime
import os
import time
from glob import glob
import ultralytics
import numpy as np
#Generic director
from Generic.Director.GenericProjectDirector import GenericProjectDirector

#Local imports
from System.App.RTSPRecorder.RTSPRecorder import RTSPRecorder
from System.App.Scrambling.Scrambling import Scrambling
from System.App.Uploader.Uploader import Uploader
from System.App.MovementDetector.MovementDetector import MovementDetector, yolov8_warmup
#Director class
class ProjectDirector( GenericProjectDirector ):

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, ):
        """
        Class builder, all the contextual configurations are charged from the base class (borg pattern) in a shared state
        Returns:
            [None]: None
        """
        super().__init__(
                {
                    '__project': {
                        '__name': 'iot-agent',
                        '__label': 'iot-agent',
                    },
                }
            )
        
        

    
    #-----------------------------------------------------------------------------------------------------------------------------
    def __play( self, what, value_a, value_b ):
        """
        Main API starter objects flux
        """
        # vision model warmup

        #Initial procedure log
        self.ctx['__obj']['__log'].setLog( 'Iniciando ...' )
        self.ctx['__obj']['__log'].setDebug( self.ctx ) 

        
        # loading model
        self.model = ultralytics.YOLO("yolov8n.pt")
        prevtime = time.time()
        yolov8_warmup(model=self.model, repetitions=10, verbose=True)
        self.ctx['__obj']['__log'].setLog(f"Model loaded in {time.time() - prevtime} seconds")  

        #Step 01: Calling videoprocedures
        # Starting all objects
        sources=['camera1']
        #video_streams = {}
        movement_detectors = {}
        TIME_TO_UPLOAD = 5 # Upload every 5 minutes
        TIME_TO_RECORD = 11 # Be active for 11 minutes
        for src in sources:
            self.ctx['__obj']['__log'].setLog('Starting {}'.format(src))
            #video_streams[src] = RTSPRecorder(src, height=480, width=640, codec='h264', verbose=True)
            movement_detectors[src] = MovementDetector(src, self.model, height=480, width=640, codec='h264', scrambling=True, verbose=True, visualize=True)
        # Record for TIME_TO_RECORD seconds
        self.ctx['__obj']['__log'].setLog('Recording for {} seconds'.format(TIME_TO_RECORD))
        for src in sources:
            #video_streams[src].startRecording()
            movement_detectors[src].start_inference()
        endTime = datetime.datetime.now() + datetime.timedelta(minutes=TIME_TO_RECORD)
        #upload all .enc files

        firstUpload = True
        uploadTime = datetime.datetime.now() + datetime.timedelta(minutes=TIME_TO_UPLOAD)
        uploader = Uploader()

        while datetime.datetime.now() < endTime:

            # upload all .enc files
            if datetime.datetime.now() > uploadTime or firstUpload:
                firstUpload = False
                self.ctx['__obj']['__log'].setLog('Uploading files')
                uploader.loadProcess()
                uploadTime = datetime.datetime.now() + datetime.timedelta(minutes=TIME_TO_UPLOAD)
                self.ctx['__obj']['__log'].setLog('Finished uploading files')
            # keep recording
            time.sleep(1)

        for src in sources:
             # close all
            #video_streams[src].release()
            movement_detectors[src].stop()
            self.ctx['__obj']['__log'].setLog('Stopped {}'.format(src))
            #encrypt records
            #self.ctx['__obj']['__log'].setLog('Encrypting records of {}'.format(src))
            #scrambler.encryptFile(video_streams[src].filename)
            
        self.ctx['__obj']['__log'].setLog('Finished demo')
        #Bye
        return None
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def setFlux( self, argv ):
        """
        Main API starter objects multiprocessing
        """
        #Main argument
        try:
            what = argv[1]
        except:
            what = None
        #Complementary argument A
        try:
            value_a = argv[2]
        except:
            value_a = None
        #Complementary argument B
        try:
            value_b = argv[3]
        except:
            value_b = None
        #Regular conciliation procedure?
        if (
            what is None or
            what == '-d' 
        ):
            """
                * Examples that you can run on console/shell:
                    a) [ python main.py -d yyyy-mm-dd yyyy-mm-dd ]
                    b) [ python main.py -d yyyy-mm-dd ]
                    c) [ python main.py ] --> This will be TODAY date
            """
            #Playing main conciliation
            self.__play(
                (
                    '-d' if what is None else what 
                ), 
                value_a, 
                value_b 
            )
        #Invalid argument?
        else:
            #Invalid execution argument log
            self.ctx['__obj']['__log'].setLog( 'Argumento de execucion [' + str( what ) + '] invalido' )
        #Goodbye
        return None
    
    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def go( argv ):
        """
        Main API starting flux
        """
        ProjectDirector().setFlux( argv )
