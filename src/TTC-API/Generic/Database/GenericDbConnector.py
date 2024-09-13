#Enviroment imports
import os
import sys

#Py modules imports
import urllib.parse
import pymysql
import psycopg2

#Oracle connector manager
import cx_Oracle

#Py modules from imports
from sqlalchemy import create_engine

#Singleton class to avoid multiple DBMS connection pointers/calls
class GenericDbConnector( ):

    #Globals cursors
    __globals = None

    #DBMS connector pointers
    __connector = {
        #DBMS repositories connection pointers
        'standard': {
            '_driver': '?',
            '_connection': 0,
            '_cursor': 0,
            '_sqlalchemy_cursor': 0,
        },
    }

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        #Setting globals
        self.__globals = globals
        #Setting connection store collection
        conn_store = {}
        #Walking connectors to be set
        for connection_name in self.__connector:
            #Getting the associated server connection config, per iterm
            conn_server = self.__globals['__config'].get( 'dbconn_' + connection_name )
            #If connector is abled, the procedure continues
            if str( conn_server['abled'] ) == '1':
                #Getting connection configuration, per item
                conn_config = self.__globals['__config'].get( conn_server['server'] )
                #Storing a helper with the server located
                if conn_server['server'] in conn_store:
                    #Re-assigning connector
                    self.__connector[connection_name] = conn_store[conn_server['server']]
                else:
                    #Getting the new connection
                    self.__connector[connection_name] = self.__getConnectionObj( conn_config )
                    #Storing (for possible sharings) the new pointer into conn_store
                    conn_store[conn_server['server']] = self.__connector[connection_name] 
            #Disabled connection log message then
            else:
                self.__globals['__log'].setLog( 
                    'La conexion [dbconn_' + connection_name + '] esta desabilitada en el archivo .config' 
                )
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __getConnectionObj( self, conn_config ):
        """
        Creates and return a dict with all connection objects proper to the connection configuration sent
        Args:
            conn_config ([dict]): Configurations to build the connection cursor object
                                    Like:
                                    (
                                        * Making connection cursor:
                                            'HOST:[' + conn_config['host'] + '] ' +
                                            'PORT:[' + conn_config['port'] + '] ' +
                                            'DBNM:[' + conn_config['database'] + ']'
                                    )
        Returns:
            [mixed]: A dict with all connection config objects or None
        """
        #DBMS is MySQL?
        if conn_config['dbms'] == 'mysql':
            #Driver is python pymysql?
            if conn_config['driver'] == 'py:pymysql':
                #Setting a MySQL connection    
                conn = (
                    pymysql.connect(
                        host = conn_config['host'],
                        port = int( conn_config['port'] ),
                        user = conn_config['user'],
                        password = conn_config['password'],
                        db = conn_config['database']
                    )
                )
                #Setting the connected driver, connection and db cursor
                return {
                    '_driver': conn_config['dbms'],
                    '_connection': conn,
                    '_cursor': conn.cursor(),
                    '_sqlalchemy_cursor': create_engine(
                        'mysql+pymysql://' + 
                        urllib.parse.quote_plus( conn_config['user'] ) + ':' + 
                        urllib.parse.quote_plus( conn_config['password'] ) + '@' + 
                        urllib.parse.quote_plus( conn_config['host'] ) + ':' + 
                        urllib.parse.quote_plus( conn_config['port'] ) + '/' + 
                        urllib.parse.quote_plus( conn_config['database'] )
                    ),
                }
        #DBMS is Oracle?
        if conn_config['dbms'] == 'oracle':
            #Driver is python cx_Oracle?
            if conn_config['driver'] == 'py:cx_Oracle':
                #Getting instant client path by platform
                os_platform = str( sys.platform ).lower()
                #Possible platform values
                """
                Possible values from sys.platform?
                ---------------------------------------------
                │ Linux               │ linux or linux2 (*) │
                │ Windows             │ win32               │
                │ Windows             │ win64               │
                │ Windows/Cygwin      │ cygwin              │
                │ Windows/MSYS2       │ msys                │
                │ Mac OS X            │ darwin              │
                │ OS/2                │ os2                 │
                │ OS/2 EMX            │ os2emx              │
                │ RiscOS              │ riscos              │
                │ AtheOS              │ atheos              │
                │ FreeBSD 7           │ freebsd7            │
                │ FreeBSD 8           │ freebsd8            │
                │ FreeBSD N           │ freebsdN            │
                │ OpenBSD 6           │ openbsd6            │
                ---------------------------------------------
                https://stackoverflow.com/questions/446209/possible-values-from-sys-platform
                """
                #On linux?
                if 'linux' in os_platform:
                    instantclient_dir = str( conn_config['instantclient_linuxos'] )
                #On windows?
                elif 'win' in os_platform:
                    instantclient_dir = str( conn_config['instantclient_windows'] )
                #Other OS?
                else:
                    instantclient_dir = str( conn_config['instantclient_otheros'] )
                #Connection only if instantclient_dir has a valid path
                if not os.path.isdir( instantclient_dir ):
                    #Ups, instantclient path trouble: raise ValueError( ... )?
                    self.__globals['__log'].setLog(
                        (
                            'La ruta [instantclient_dir]=[' + instantclient_dir + '] ' +
                            'para la conexion Oracle es invalida o no existe'
                        ),
                        code = 404,
                        type = 'error'
                    )
                #Enviroment var setting
                #os.environ['LD_LIBRARY_PATH'] = instantclient_dir
                if 'LD_LIBRARY_PATH' in os.environ:
                    self.__globals['__log'].setLog( 
                        'Variable de entorno cx_Oracle [LD_LIBRARY_PATH]: ' + str( os.environ['LD_LIBRARY_PATH'] ) 
                    )
                else:
                    self.__globals['__log'].setLog(
                        (
                            'Variable de entorno cx_Oracle os.environ["LD_LIBRARY_PATH"] no encontrada'
                        ),
                        type = 'warning'
                    )
                #Oracle client inits
                try:
                    cx_Oracle.init_oracle_client( lib_dir = instantclient_dir )
                except:
                    self.__globals['__log'].setLog(
                        'Atrapando excepcion con Client Oracle [cx_Oracle.init_oracle_client]: ya habia sido establecido' 
                    )
                #Connection standard
                try:
                    #Trying to DSN and Connect
                    conn = (
                        cx_Oracle.connect(
                            user = conn_config['user'],
                            password = conn_config['password'],
                            dsn = (
                                #DSN
                                cx_Oracle.makedsn(
                                    conn_config['host'], 
                                    conn_config['port'], 
                                    service_name = conn_config['service_name']
                                )
                            )
                        )
                    )
                    #Cursor setted
                    cursor = conn.cursor()
                    #Basic log
                    self.__globals['__log'].setLog( 'Conexion [cx_Oracle] y cursor creados correctamente' )
                except Exception as e:
                    #Ups, connection trouble
                    self.__globals['__log'].setLog(
                        (
                            'Error CX001 al conectar con [cx_Oracle]: ' + str( e )
                        ),
                        code = 500,
                        type = 'error'
                    ) 
                    #And null connection vars
                    conn = cursor = None
                #Connection with sqlalchemy
                try:
                    #Alchemy engine
                    engine = (
                        create_engine(
                            'oracle+cx_oracle://' + 
                            urllib.parse.quote_plus( conn_config['user'] ) + ':' + 
                            urllib.parse.quote_plus( conn_config['password'] ) +'@' + 
                            urllib.parse.quote_plus( conn_config['host'] ) + ':' + 
                            str( urllib.parse.quote_plus( conn_config['port'] ) ) + 
                            '/?service_name=' + urllib.parse.quote_plus( conn_config['service_name'] )
                        )
                    )
                    #Engine log
                    self.__globals['__log'].setLog( 
                        'Engine [sqlalchemy] + [cx_Oracle] listo para usarse, pero aun por probar su conectividad' 
                    )
                except Exception as e:
                    #Ups, sqlalchemy trouble
                    self.__globals['__log'].setLog(
                        (
                            'Error CX002 al crear [sqlalchemy] + [cx_Oracle] engine: ' + str( e )
                        ),
                        code = 500,
                        type = 'error'
                    )
                    #And null engine
                    engine = None
                #Setting the connected driver, connection and db cursor
                return {
                    '_driver': conn_config['dbms'],
                    '_connection': conn,
                    '_cursor': cursor,
                    '_sqlalchemy_cursor': engine,
                }
        #DBMS is PostgreSQL?
        if conn_config['dbms'] == 'postgresql':
            #Driver is python psycopg2?
            if conn_config['driver'] == 'py:psycopg2':
                #Setting a PostgreSQL connection
                conn = (
                    psycopg2.connect(
                        host = conn_config['host'],
                        port = int( conn_config['port'] ),
                        user = conn_config['user'],
                        password = conn_config['password'],
                        database = conn_config['database']
                    ) 
                )               
                #Setting the connected driver, connection and db cursor
                return {
                    '_driver': conn_config['dbms'],
                    '_connection': conn,
                    '_cursor': conn.cursor(),
                    '_sqlalchemy_cursor': create_engine(
                        'postgresql+psycopg2://' + 
                        urllib.parse.quote_plus( conn_config['user'] ) + ':' + 
                        urllib.parse.quote_plus( conn_config['password'] ) + '@' + 
                        urllib.parse.quote_plus( conn_config['host'] ) + ':' + 
                        urllib.parse.quote_plus( conn_config['port'] ) + '/' + 
                        urllib.parse.quote_plus( conn_config['database'] )
                    ),
                }
        #No matches?, nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __getConnection( self, connector_name ):
        """
        Sets this channel data... if the row can match it...
        Args:
            connector_name ([string]): Connector name to pick. Can be: 
                                       [payment_report_main], 
                                       [postnotie_main], 
                                       [dwd_channel_main], 
                                       [gtim_main] or 
                                       [ALL]
        Returns:
            [mixed]: None if the connection name is INVALID,
                     A connection pointer if the connection name is VALID, or
                     A dictionary with ALL pointers if the connection name is "ALL"
                     * Note: The connection pointer could be 0 if this is not "ready"
        """
        #All connections
        if connector_name == 'ALL':
            return self.__connector
        #An specific connection
        if connector_name in self.__connector:
            return self.__connector[connector_name]
        #No matches go back :(
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def getConnection( self, connector_name ):
        """
        Sets this channel data... if the row can match it...
        Args:
            connector_name ([string]): Connector name to pick. Can be: 
                                       [payment_report_main], 
                                       [postnotie_main], 
                                       [dwd_channel_main], 
                                       [main] or 
                                       [ALL]
        Returns:
            [mixed]: None if the connection name is INVALID,
                     A connection pointer if the connection name is VALID, or
                     A dictionary with ALL pointers if the connection name is "ALL"
        """
        #Singleton object call, this do not generates an instance per call. It's the same instance than applies for each call!
        return self.__getConnection( connector_name )
