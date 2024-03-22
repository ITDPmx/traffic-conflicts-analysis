
#Generic db driver mysql
from Generic.Database.Driver.GenericMySql import GenericMySql

#Singleton class to avoid multiple DBMS connection pointers/calls
class MySql( GenericMySql ):

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        return super().__init__( globals )
