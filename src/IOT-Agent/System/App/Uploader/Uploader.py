import time
import boto3
from glob import glob
import os
import asyncio
import requests
#Local imports
from Generic.Global.Borg import Borg

#Director class
class Uploader(Borg):

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
        self.aws = self.ctx['__obj']['__config'].get('aws')
        session = boto3.Session(aws_access_key_id= self.aws['access_key_id'],
                               aws_secret_access_key= self.aws['secret_access_key'],
                               region_name= self.aws['region_name']
                              )
        self.s3 = session.resource('s3')
        self.bucket = self.s3.Bucket(self.aws['bucket'])
        self.s3_client = boto3.client('s3',
                        aws_access_key_id= self.aws['access_key_id'],
                        aws_secret_access_key= self.aws['secret_access_key'],
                        )
        self.API_URL = self.ctx['__obj']['__config'].get('ctx_broker')['url']
        #Bye
        return None
    #---------------------------------------------------------------------------------------------------------------------------------
    def createDir(self, camera: str = 'camera1') -> None:
        """
        This method construct a directory path in S3.

        Args:
            camera [str]
        Returns:
            None
        """
        GP = self.ctx['__obj']['__global_procedures']
        self.path = 'records/' + GP.getTodayString("%Y_%m_%d") + f'/{camera}/'
        exist = False
        #verify if directory path exist
        for obj in self.bucket.objects.all():
            if obj.key == self.path:
                exist = True
        #create directory path in bucket
        if not exist:
            self.bucket.put_object(Key=self.path)
            #validate the creation of dir
            for obj in self.bucket.objects.all():
                if obj.key == self.path:
                    self.ctx['__obj']['__log'].setLog(f'The directory {self.path} has been created successfully')
        else:
            self.ctx['__obj']['__log'].setLog(f'The directory {self.path} already exist')

        #bye
        return None
    

    def upFile(self, file_path: str = None) -> None:
        """
        This method upload a file in a directory path in S3.

        Args:
            path [list]
        Returns:
            None
        """
        if file_path == None:
            self.ctx['__obj']['__log'].setLog(f'You need to specify the file to upload')
            return
        base_file = os.path.basename(file_path)
        self.path = os.path.dirname(file_path[file_path.index('records'):]) + '/'
        #verify if the file already exist
        exist = False
        for obj in self.s3_client.list_objects(Bucket=self.aws['bucket'])['Contents']:
            if obj['Key'] == self.path + base_file:
                exist = True
        #upload the file
        if not exist:
            self.s3_client.upload_file(file_path, self.aws['bucket'], self.path + base_file)
            #validate that the file has been already uploaded
            for obj in self.s3_client.list_objects(Bucket=self.aws['bucket'])['Contents']:
                if obj['Key'] == self.path + base_file:
                    self.ctx['__obj']['__log'].setLog(f'The file {base_file} has been uploaded successfully')
                    #create entity
                    try:
                        id_camera = int(file_path[file_path.index('camera') + 6])
                    except ValueError:
                        self.ctx['__obj']['__log'].setLog(f'Failed getting id camera')
                        return None
                    asyncio.run(self.create_entity(id_camera, self.path + base_file))
        else:
            self.ctx['__obj']['__log'].setLog(f'The file {base_file} already exist')
        #bye
        return None
    
    async def create_entity(self, cam_id: int, file: str) -> None:
        """
        This method calls an endpoint API to create entity of captured video in context broker.

        """
        # Create camera entity in API
        camera_data = dict(id=cam_id, bucket="tec-crowd-counting", file=file)
        response = requests.post(f"{self.API_URL}/camera_footage", json=camera_data)
        camera_entity = response.json()
        self.ctx['__obj']['__log'].setLog(f'The following entity has been created: {camera_entity}')
    
    def loadProcess(self) -> None:
        """
        This method upload all .enc files and delete them from records folder.

        Args:
            None
        Returns:
            None
        """

        files = glob('records/**/*.enc',recursive=True)
        for f in files:
            self.ctx['__obj']['__log'].setLog(f'Uploading {f}')
            self.upFile(f)
            os.remove(f)
         