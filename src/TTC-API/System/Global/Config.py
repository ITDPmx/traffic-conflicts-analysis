
from Generic.Global.GenericConfig import GenericConfig

#Configuration class
class Config( GenericConfig ):
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the configurations are made just once (singleton class)
        Returns:
            [None]: None
        """
        return super().__init__( globals )
