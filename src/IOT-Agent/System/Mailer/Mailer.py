
#Generic mailer
from Generic.Mailer.GenericMailer import GenericMailer

#Singleton class to avoid multiple DBMS connection pointers/calls
class Mailer( GenericMailer ):

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the configurations are made just once (singleton class)
        Returns:
            [None]: None
        """
        return super().__init__( globals )
