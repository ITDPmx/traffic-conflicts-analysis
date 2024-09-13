
#Generic log
from Generic.Global.GenericLog import GenericLog

#Mainn log class
class Log( GenericLog ):

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the configurations are made just once (singleton class)
        Returns:
            [None]: None
        """
        return super().__init__( globals )
