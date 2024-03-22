
#Generic db connector
from Generic.Database.GenericDbConnector import GenericDbConnector

#Singleton class to avoid multiple DBMS connection pointers/calls
class DbConnector( GenericDbConnector ):

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        return super().__init__( globals )
