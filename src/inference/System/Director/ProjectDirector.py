import datetime
import os
import time
import requests
import json
from glob import glob
#Generic director
from Generic.Director.GenericProjectDirector import GenericProjectDirector

#Local imports
from System.App.InferProcedures.InferProcedures import InferProcedures
import asyncio


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
        #self.orion = OrionProcedures()
        
        

    #-----------------------------------------------------------------------------------------------------------------------------
    async def __play( self, what, value_a, value_b ):
        """
        Main API starter objects flux
        """
        # vision model warmup

        #Initial procedure log
        self.ctx['__obj']['__log'].setLog( 'Iniciando ...' )
        self.ctx['__obj']['__log'].setDebug( self.ctx ) 

    	#get entities to infer
        camera_entities = requests.post("http://127.0.0.1:8000/ent2infer", 
                                 headers={'Content-Type':'application/json'
                                         }).json()
        print(camera_entities[0]['root'].keys())
        if len(camera_entities)>0:
            self.ctx['__obj']['__log'].setLog( f'Se van a inferir {len(camera_entities)} entidades' )
            # Infer all entities
            infer = InferProcedures()
            person_entities = await infer.create_person_entities(camera_entities)
        else:
            self.ctx['__obj']['__log'].setLog( 'No hay entidades que inferir' )
        self.ctx['__obj']['__log'].setLog('Terminado ')
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
            asyncio.run(self.__play(
                (
                    '-d' if what is None else what 
                ), 
                value_a, 
                value_b 
            ))
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
