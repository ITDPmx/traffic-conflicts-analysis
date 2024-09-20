import datetime
import os
import time
from glob import glob
import numpy as np
import requests

#Generic director
from Generic.Director.GenericProjectDirector import GenericProjectDirector

#AWS
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

#Local imports
from System.App.OBBDetector.OBBDetector import OBBDetector
from System.App.OBBVisualization.OBBVisualization import OBBVisualization
from System.App.TrajsProcessor.TrajsProcessor import TrajsProcessor
from System.App.CollisionDataProcessor.CollisionDataProcessor import CollisionDataProcessor

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

        load_dotenv()
        AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") 
        AWS_BUCKET_NAME = 'homography-matrices'
        AWS_REGION = 'us-east-2'

        self.S3_CLIENT = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        ) 
        
    #-----------------------------------------------------------------------------------------------------------------------------
    def __play( self, what, id_video ):
        """
        Main API starter objects flux
        """
        # vision model warmup

        #Initial procedure log
        self.ctx['__obj']['__log'].setLog( 'Iniciando ...' )
        self.ctx['__obj']['__log'].setDebug( self.ctx ) 

        prevtime = time.time()

        # Get video from bucket
        # os.makedirs('videos', exist_ok=True)
        # new_path = "videos/test"
        # self.S3_CLIENT.download_file(bucket, path, new_path)
        
        # obb detector 
        video_path = '/shared_data/bev_' + id_video + '.mp4'
        # video_path = 'videos/181653_cam3_bev.mp4'
        # bev_path = "/shared_data/bev_" + id_video + ".mp4"
        model_path = "weights/yolov9e-seg.pt"
        model_obb_path = "weights/yolo_obb.pt"
        model_WHE_path = 'weights/best_width_height_estimator.pth'
        obb_processor = OBBDetector(video_path, id_video, model_path, model_obb_path, model_WHE_path)
        df = obb_processor.process_video()
        self.ctx['__obj']['__log'].setLog(f"Video {video_path} processed in {time.time() - prevtime} seconds")  
        # Check if df is empty
        if df.empty:
            print("There are no detections in the video.")
            return None
        else: 
            print("There were " + str(len(df)) + " detections in the video.")

        #Step 02: Calling Trajs processor
        prevtime = time.time()
        trajs_processor = TrajsProcessor(df)
        trajs_processor.preprocess()
        trajs_processor.correct_by_velocity()
        trajs_processor.correct_coordinates()
        trajs_processor.interpolate_data()
        self.ctx['__obj']['__log'].setLog(f"Trajectories processed in {time.time() - prevtime} seconds")  
        df = trajs_processor.df

        df.to_csv('/shared_data/df.csv')

        

        #Step 03: Calling OBB visualization

        output_path = '/shared_data/obb_processed.mp4'
        # output_path = 'processed_videos/video' + id_video + '.mp4'
        obbvis = OBBVisualization(video_path, output_path, df)
        obbvis.process_video()
        bucket_path = 'processed_videos/video' + id_video + '.mp4'
        obb_processor.uploadFile(output_path, bucket_path)
        response = requests.post('https://tca.mexico.itdp.org/api/progress', json={"id": id_video, "progress": 95 })

        """
        #Step 04: Calling TTC Estimator

        colProc = CollisionDataProcessor(df)
        colProc.preprocess_data()
        colProc.generate_pairs()
        colProc.calculate_ttc()
        colProc.calculate_severity()
        colProc.filter_data()
        colProc.aggregate_data()
        colProc.save_to_csv()
        col_file = 'reports/collision_data' + id_video + '.csv'
        summary_file = 'reports/collision_data_summary' + id_video + '.csv'
        obb_processesor.uploadFile(col_file, 'csvs/collision_data.csv')
        obb_processesor.uploadFile(summary_file, 'csvs/collision_data_summary.csv')
        response = requests.post('https://tca.mexico.itdp.org/api/progress', json={"id": id_video, "progress": 100 })
        """
        self.ctx['__obj']['__log'].setLog('Finished')
        #Bye
        return None
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def setFlux( self, argv, id_video):
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
                id_video
            )
        #Invalid argument?
        else:
            #Invalid execution argument log
            self.ctx['__obj']['__log'].setLog( 'Argumento de execucion [' + str( what ) + '] invalido' )
        #Goodbye
        return None
    
    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def go( argv, id_video ):
        """
        Main API starting flux
        """
        ProjectDirector().setFlux( argv, id_video)
