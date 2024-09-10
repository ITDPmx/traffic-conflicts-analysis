
#Generic entity
from Generic.Database.Entity.GenericEntity import GenericEntity

#Singleton class to avoid multiple DBMS connection pointers/calls
class Entity( GenericEntity ):

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, config, globals ):
        return super().__init__( config, globals )
