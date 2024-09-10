
#Generic db manager
from Generic.Database.GenericDbManager import GenericDbManager

#Singleton class to avoid multiple DBMS connection pointers/calls
class DbManager( GenericDbManager ):
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the connections are made just once at this step
        Returns:
            [None]: None
        """
        return super().__init__( globals )
