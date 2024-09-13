import sys, traceback

#Local imports
from Generic.Global.Borg import Borg

#Childs imports to easy "base" performs
from System.Global.GlobalProcedures import GlobalProcedures
from System.Global.Config import Config
from System.Global.Log import Log
from System.Database.Driver.MySql import MySql
from System.Database.DbConnector import DbConnector
from System.Database.DbManager import DbManager
from System.Mailer.Mailer import Mailer


#Auto ingestor class for this file/section
class GenericProjectDirector( Borg ):

    #Contextual repository
    ctx = None

    #Child configurations container
    __child_config = None

    #Flag to check if the syetem exception hook is already done!
    __exception_hooked = False

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, child_config ):
        """
        Class builder, all the configurations are made just once (singleton class)
        Returns:
            [None]: None
        """
        #Borg pattern constructor
        super().__init__()
        #Child configurations assignation
        self.__child_config = child_config
        #Global procedures
        __global_procedures = GlobalProcedures()
        #Configuration cursor
        __config = (
            Config(
                {
                    '__global_procedures': __global_procedures,
                }
            )
        )
        #Log cursor
        __log = (
            Log(
                {
                    '__global_procedures': __global_procedures,
                    '__config': __config,
                }
            )
        )
        #Setting the local error handler
        self.__setLocalExceptionHandler( __log )
        #Getting context info by init base objects
        self.ctx = self.__initDataBaseObjectsAndGetAllContext( __global_procedures, __config, __log )

        #Bye
        return None
   
    #-----------------------------------------------------------------------------------------------------------------------------
    def __initDataBaseObjectsAndGetAllContext( self, __global_procedures, __config, __log ):
        #Global attributes
        globals = (
            {
                '__global_procedures': __global_procedures,
                '__config': __config,
                '__log': __log,
            }
        )
        #Db connector cursor
        __db_connector = DbConnector( globals )

        #Db MySQL driver cursor
        __driver_mysql = MySql( globals )
        #Appending the new objects to globals
        globals['__db'] = (
            {
                '__connector': __db_connector,
                '__mysql': {
                    '__driver': __driver_mysql,
                },
            }
        )
        #Db manager cursor
        __db_manager = DbManager( globals )
        #Apending the db manager to globals
        globals['__db']['__manager'] = __db_manager
        #Mailer manager cursor
        __mailer = Mailer( globals )
        #Setting mailer pointer on globals
        globals['__mailer'] = __mailer
        #Context go back
        return {
            #Objects
            '__obj': {
                '__global_procedures': __global_procedures,
                '__config': __config,
                '__log': __log,
                '__mailer': __mailer,
                '__db': {
                    '__connector': __db_connector,
                    '__manager': __db_manager,
                    '__mysql': {
                        '__driver': __driver_mysql,
                    },
                }
            },
            #All director configurations
            '__config': (
                __global_procedures.mergeDicts(
                    #First dict with child class configurations
                    self.__child_config,
                    #Second dict with complementary info
                    {
                        '__global_run_id': __log.getGlobalRunId(),
                        '__datetime': __global_procedures.getTodayDatetime(),
                    }
                )
            ),
        }

   
    #-----------------------------------------------------------------------------------------------------------------------------
    def __setLocalExceptionHandler( self, log ):
        """
        Sets the API local exception handler
        """
        #Exception handler is already done?
        if not self.__exception_hooked:
            #Handling this class exception hook
            self.__exceptionHook( log )
            #No more hooks try
            self.__exception_hooked = True
        #Go back with nothing
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __exceptionHook( self, log, python_error_print_active = True ):
        #Local definition 
        def exceptionHook( exctype, value, trace ):
            #Getting the traceback formatted message
            traceback_message = ''
            for line in traceback.format_tb( trace ):
                traceback_message += str( line )
            #Text to be log
            log_text = (
                'PYTHON-EXCEPTION:' + '\n\n' +
                '>>>>>>>>>>>>>>>[TRACEBACK]<<<<<<<<<<<<<<<' + '\n\n' +
                traceback_message + '\n'
                '>>>>>>>>>>>>>>[ERROR_DESC]<<<<<<<<<<<<<<<' + '\n\n' +
                '  [' + exctype.__name__ + ']:' + str( value ) + '\n\n' +
                '>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<' + '\n'
            )
            #Setting the log entry on file
            log.setLog(
                log_text,
                type = 'exception',
                code = 500,
                print_on_console = False
            )
            #Printing local python message too
            if python_error_print_active :
                sys.__excepthook__( exctype, value, traceback )
        #Hook overwritting
        sys.excepthook = exceptionHook
        #Nothing go back
        return None
