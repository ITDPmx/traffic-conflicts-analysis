import datetime
import os
import time
from glob import glob
import numpy as np
#Generic director
from Generic.Director.GenericProjectDirector import GenericProjectDirector

#Local imports
from System.App.OBBDetector.OBBDetector import OBBDetector
from System.App.OBBVisualization.OBBVisualization import OBBVisualization
from System.App.TrajsProcessor.TrajsProcessor import TrajsProcessor

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

        prevtime = time.time()
        # obb detector 
        video_path = "videos/181653_cam3_bev.mp4"
        model_path = "weights/yolov9e-seg.pt"
        model_obb_path = "weights/yolo_obb.pt"
        model_WHE_path = 'weights/best_width_height_estimator.pth'
        obb_processor = OBBDetector(video_path, model_path, model_obb_path, model_WHE_path)
        df = obb_processor.process_video()
        self.ctx['__obj']['__log'].setLog(f"Video {video_path} processed in {time.time() - prevtime} seconds")  

        #Step 02: Calling Trajs processor
        prevtime = time.time()
        trajs_processor = TrajsProcessor(df)
        trajs_processor.preprocess()
        trajs_processor.correct_by_velocity()
        trajs_processor.correct_coordinates()
        trajs_processor.interpolate_data()
        self.ctx['__obj']['__log'].setLog(f"Trajectories processed in {time.time() - prevtime} seconds")  
        df = trajs_processor.df

        #Step 03: Calling OBB visualization

        output_path = 'videos/obb_processed.mp4'
        obbvis = OBBVisualization(video_path, output_path, df)
        obbvis.process_video()

        self.ctx['__obj']['__log'].setLog('Finished')
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
