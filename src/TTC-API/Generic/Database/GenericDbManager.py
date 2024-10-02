import pandas as Panda


#Singleton class to avoid multiple DBMS connection pointers/calls
class GenericDbManager( ):
    
    #Globals cursors
    __globals = None

    #DBMS connector pointers
    __connector = None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the connections are made just once at this step
        Returns:
            [None]: None
        """
        #Globals cursors pointers
        self.__globals = globals
        #Getting connections from connector
        self.__connector = self.__globals['__db']['__connector'].getConnection( 'ALL' )
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __logMessage( self, style, type, connection_name, message_for ):
        """
        Executes a query for the connection sent
        Args:
            connection_name ([string]): Connection to log for
            message_for ([string]): SQL string code to be executed
        Returns:
            [None]: None
        """
        #Notice
        if style == 'notice':
            #Generic message
            if type == 'generic':
                self.__globals['__log'].setLog( message_for )
            #Entity builded
            if type == 'entity_builded':
                self.__globals['__log'].setLog( 'Para conexion db [' + connection_name + '] ' + message_for )
        #Error
        if style == 'error':
            #Invalid connection driver
            if type == 'connection_driver':
                self.__globals['__log'].setLog(
                    (
                        'GenericDbManager dice:' +
                        '\n--------------------------------- Driver de conexion invalido -------------\n' + 
                        'La conexion [' + connection_name + '] no tiene un driver DBMS valido para realizar ' +
                        '[' + message_for + ']\n' +
                        'Todos los procesos para [' + message_for + '] han sido detenidos\n'
                    ),
                    code = 404,
                    type = 'error'
                )                
            #Invalid sqlalchemy cursor
            elif type == 'sqlalchemy_cursor':
                self.__globals['__log'].setLog(
                    (
                        'GenericDbManager dice:' +
                        '\n--------------------------------- Cursor [sqlalchemy] invalido -------------------------\n' +
                        'No se puede salvar el Panda para la conexion [' + connection_name + '].\n' +
                        'La conexion no tiene cursor SQLAlchemy [_sqlalchemy_cursor]\n' +
                        message_for
                    ),
                    code = 404,
                    type = 'error'
                )
        #Nothing go back
        return None  
   
    #-----------------------------------------------------------------------------------------------------------------------------
    def __executeQueryFor( self, connection_name, sql, vars ):
        """
        Executes a query for the connection sent
        Args:
            connection_name ([string]): Connection to perform
            sql ([string]): SQL string code to be executed
            vars ([dict]): Dictionary of SQL variables to parse
                           Example:
                           ...
                           sql_string = 'SELECT ... FROM ... WHERE some_field = %(_some_field)s ... '
                           ...
                           vars = {
                                '_some_field': 'VALUE TO SET',
                                ...,
                           }
        Returns:
            [int]: Number fo afeccted records
        """
        #Escape if the SQL is None
        if not ( sql is None ):
            #If builder is for MySQL
            if self.__connector[connection_name]['_driver'] == 'mysql':
                return (
                    self.__globals['__db']['__mysql']['__driver'].executeQuery(
                        self.__connector[connection_name], 
                        sql, 
                        vars 
                    )
                )
        #Invalid driver?
        self.__logMessage( 'error', 'connection_driver', connection_name, 'GenericDbManager.__executeQueryFor' )
        #Nope, nothing to execute
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __playQueryFor( self, connection_name, sql, vars, response_type = 'native' ):
        """
        Gets an SQL query for the connector pointer sent
        Args:
            connector_name ([string]): Connector name to pick. Can be: 
                                       [payment_report_main], 
                                       [postnotie_main], 
                                       [dwd_channel_main] or
                                       [main]            
            sql ([string]): SQL string query
            vars ([dict]): Dictionary of SQL variables to parse
                           Example:
                           ...
                           sql_string = 'SELECT ... FROM ... WHERE some_field = %(_some_field)s ... '
                           ...
                           vars = {
                                '_some_field': 'VALUE TO SET',
                                ...,
                           }
        Returns:
            [mixed]: None if the query is invalid, or the SQL query result
        """
        #If builder is for MySQL
        if self.__connector[connection_name]['_driver'] == 'mysql':
            #Native way
            if response_type == 'native':
                return (
                    self.__globals['__db']['__mysql']['__driver'].playQuery( 
                        self.__connector[connection_name], 
                        sql, 
                        vars 
                    )
                )
            #Pandas way
            elif response_type == 'panda':
                return (
                    Panda.read_sql(
                        sql, 
                        con = self.__connector[connection_name]['_sqlalchemy_cursor'],
                        params = vars
                    )
                )
        elif self.__connector[connection_name]['_driver'] == 'postgresql':
            #Native way
            if response_type == 'native':
                return (
                    self.__globals['__db']['__mysql']['__driver'].playQuery( 
                        self.__connector[connection_name], 
                        sql, 
                        vars 
                    )
                )
            #Pandas way
            elif response_type == 'panda':
                return (
                    Panda.read_sql(
                        sql, 
                        con = self.__connector[connection_name]['_sqlalchemy_cursor'],
                        params = vars
                    )
                )               
        #Invalid driver?
        else:
            self.__logMessage( 'error', 'connection_driver', connection_name, 'GenericDbManager.__playQueryFor' )
        #Nothing to go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def getFullEntity( self, connection_name, entity_name, fields, response_type = 'native', alias_prefix = '' ):
        """
        Builds an entity in a database from the connection sent
        Args:
            connection_name ([string]): Connection that handles the database to perform
            entity_name ([string]): Entity name to get full data
            fields ([dict]): List of dictionaries with entity field name/data to get
            response_type ([string]): For regular response play 'native', for Panda object play 'panda'
            alias_prefix ([string]): Alias prefix for the fields sent
        Returns:
            [None]: None
        """
        if self.__connector[connection_name]['_driver'] == 'mysql':
            return (
                self.__playQueryFor(
                    connection_name,
                    (
                        self.__globals['__db']['__mysql']['__driver'].getFullEntityQuery(
                            entity_name, 
                            fields, 
                            alias_prefix 
                        )
                    ), 
                    {}, 
                    response_type 
                )
            )        
        #Invalid driver?
        else:
            self.__logMessage( 'error', 'connection_driver', connection_name, 'GenericDbManager.__getFullEntity' )
        #Response go back
        return

    #-----------------------------------------------------------------------------------------------------------------------------
    def playQueryFor( self, connection_name, sql, vars = None, response_type = 'native' ):
        """
        Gets an SQL query for the connector pointer sent 
        Args:
            connection_name ([string]): Connector name to pick. Can be: 
                                        [payment_report_main], 
                                        [postnotie_main], 
                                        [dwd_channel_main] or
                                        [main]
            sql ([string]): SQL string query
            vars ([dict]): Dictionary of SQL variables to parse
                           Example:
                           ...
                           sql_string = 'SELECT ... FROM ... WHERE some_field = %(_some_field)s ... '
                           ...
                           vars = {
                                '_some_field': 'VALUE TO SET',
                                ...,
                           }
        Returns:
            [mixed]: None if the query is invalid, or the SQL query result
        """
        return self.__playQueryFor( connection_name, sql, vars, response_type )

    #-----------------------------------------------------------------------------------------------------------------------------
    def executeQueryFor( self, connection_name, sql, vars = None ):
        """
        Executes a query for the connection sent
        Args:
            connection_name ([string]): Connector name to pick. Can be: 
                                        [payment_report_main], 
                                        [postnotie_main], 
                                        [dwd_channel_main] or
                                        [main]
            sql ([type]): SQL string code to be executed
            vars ([type]): If vars is a list or tuple, %s can be used as a placeholder in the query.
                           If vars is a dict, %(name)s can be used as a placeholder in the query.
        Returns:
            [int]: Number fo afeccted records
        """
        return self.__executeQueryFor( connection_name, sql, vars )

    #-----------------------------------------------------------------------------------------------------------------------------
    def buildEntity( self, connection_name, entity_name, fields ):
        """
        Builds an entity for the connection selected, with the entity name and fields sent
        Args:
            connection_name ([string]): Connection to perform
            entity_name ([string]): SQL string entity name
            fields ([dict]): Fields to build
        Returns:
            [None]: None
        """    
        #If builder is for MySQL 
        if self.__connector[connection_name]['_driver'] == 'mysql':
            #Building entity
            self.__globals['__db']['__mysql']['__driver'].executeEntityBuilder(
                self.__connector[connection_name],
                entity_name, 
                fields
            )
            #Logging 
            self.__logMessage(
                'notice', 
                'entity_builded', 
                connection_name, 
                (
                    '[GenericDbManager.buildEntity] dice: [' + entity_name + '] ha recibido un BUILDER-CHECK sobre la BD. ' +
                    'Puede verificar la estructura ahora.'
                )
            )
        #Invalid driver?
        else:
            self.__logMessage( 'error', 'connection_driver', connection_name, 'GenericDbManager.__buildEntity' )
        #Foreing keys try
        self.buildAllForeingKeysForAllBuildedEntities()
        #Nope go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def buildAllForeingKeysForAllBuildedEntities( self, ):
        """
        Builds all foreing keys to all entities created
        Many of this tries will catch a lot of errors, because the parent model of the m2o relation could not exist at the moment
        But this automatization is prefered by catching errors that will be solve time later, when the parent model is created
        Returns:
            [None]: Nothing
        """
        self.__globals['__db']['__mysql']['__driver'].resolveAndBuildAllEntitiesForeingKeys()
        #Nope, nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def insert( self, connection_name, entity_name, datarows ):
        """
        Inserts records
        Args:            
            connection_name ([string]): Connection to perform
            entity_name ([string]): SQL string entity name
            datarows ([list]): List of data to be set
                                Example:
                                [
                                    ...,
                                    {
                                        'entity_field_name': {
                                            'value': 'Entity value to be save',
                                            'quote': True, #Boolean to set string-quotes ('') for the [value] sent
                                        }
                                    }
                                    ...,
                                ]
        Returns:
            [int]: Number fo afeccted records
        """
        res = None
        #If builder is for MySQL 
        if self.__connector[connection_name]['_driver'] == 'mysql':
            res = (
                self.__globals['__db']['__mysql']['__driver'].insert(
                    self.__connector[connection_name],
                    entity_name, 
                    datarows
                )
            )
            #Logging 
            self.__logMessage(
                'notice', 
                'generic', 
                connection_name, 
                (
                    'Insercion SQL a entidad [' + entity_name + '] finalizada, ' +
                    'con ' + str( len( datarows ) ) + ' registro(s) insertado(s)'
                )
            )
        #Invalid driver?
        else:
            self.__logMessage( 'error', 'connection_driver', connection_name, 'GenericDbManager.__buildEntity' )
        #Nope go back
        return res

    #-----------------------------------------------------------------------------------------------------------------------------
    def getPandaCsv( self, file_name, file_path, separator = '|', converters = None ):
        """
        Returns a CSV file contents in a Panda object
        Args:
            file_name ([string]): CSV file name
            file_path ([string]): File directory path
            separator ([char]): A character that is the CSV separator
        Returns:
            [panda]: The CSV Panda object
        """
        #Generic notice: leyendo Panda desde CSV
        self.__logMessage( 'notice', 'generic', None, 'Generando Panda desde archivo CSV [' + file_name + ']' )
        #Panda go back
        return (
            Panda.read_csv(
                self.__globals['__global_procedures'].joinPath( file_path + [ file_name ] ), 
                sep = separator,
                converters = converters
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    def savePandaToDb( self, connection_name, entity_name, panda, procedure = 'insert', columns_to_save = None ):
        """
        Saves the panda dataframe to the database, in the connection and entity sent
        Args:
            connection_name ([string]): Connector name to pick. Can be: 
                                        [payment_report_main], 
                                        [postnotie_main], 
                                        [dwd_channel_main] or
                                        [main]            
            entity_name ([string]): Entity SQL name
            panda ([panda]): Panda to be save
            procedure ([string]): To execute INSERT or UPDATE dataframe info into entity sent
            columns_to_save ([list]): Of columns to be saved
        Returns:
            [dict]: Status result
        """
        #Invalid sqlalchemy connector?
        if self.__connector[connection_name]['_sqlalchemy_cursor'] is None:
            self.__logMessage(
                'error', 
                'sqlalchemy_cursor', 
                connection_name, 
                'En la entidad: [' + entity_name + '] in [GenericDbManager.__savePandaToDb]' 
            )
        #All ok?, save then
        else:
            #Setting the columns to play if is right
            if not ( columns_to_save is None ):
                panda_cols = list( panda.columns )
                wrong_cols = []
                #Walking valid columns and remove obsolete/invalid columns
                for panda_col in panda_cols:
                    if not ( panda_col in columns_to_save ):
                        wrong_cols.append( panda_col )
                #Bad columns goodbye
                panda = panda.drop( columns = wrong_cols )
            #Procedure standard
            std_procedure = procedure.lower()
            #Trying to set the INSERT procedure
            if std_procedure == 'insert':
                try:
                    panda.to_sql(
                        name = entity_name,
                        con = self.__connector[connection_name]['_sqlalchemy_cursor'],
                        if_exists = 'append',
                        index = False
                    )
                except Exception as e:
                    return {
                        'status': 500,
                        'eerror': e
                    }
            #Trying to set the UPDATE procedure
            elif std_procedure == 'update':
                #Connection cursor
                cursor = self.__connector[connection_name]['_sqlalchemy_cursor']
                #Temporal table name
                temp_entity = '__tmp_' + str( self.__globals['__global_procedures'].getMD5UniqueIntOfValue( entity_name ) )
                #SQL update fields string from temp to entity
                sql_fields = ''
                for field in list( panda.columns ):
                    if field != 'id':
                        sql_fields += ( ', ' if sql_fields else '' ) + 'e.' + str( field ) + ' = t.' + str( field )
                #Appending into temporal table
                try:
                    #Appending into temporal table
                    panda.to_sql(
                        name = temp_entity,
                        con = cursor,
                        if_exists = 'replace',
                        index = False
                    )
                    #Updating by connection
                    with cursor.begin() as connection:
                        #Final update from temp to entity
                        connection.execute(
                            """
                                UPDATE 
                                    """ + entity_name + """ AS e,
                                    """ + temp_entity + """ AS t
                                SET 
                                    """ + sql_fields + """
                                WHERE
                                    e.id = t.id
                            """
                        )
                        #And dropping the temporary table
                        connection.execute(
                            """
                                DROP TABLE """ + temp_entity + """
                            """
                        )
                except Exception as e:
                    return {
                        'status': 500,
                        'eerror': e
                    }
            else:
                std_procedure = None
            #Invalid procedure?
            if std_procedure is None:
                return {
                    'status': 500,
                    'eerror': 'Procedimiento [' + procedure + '] es invalido para el salvado de objeto panda en [savePandaToDb]'
                }
            #Generic notice: 
            self.__logMessage( 'notice', 'generic', None, 'Entidad [' + entity_name + '] salvada desde objeto Panda' )
        #Nothing go back
        return {
            'status': 200,
            'eerror': None
        }
