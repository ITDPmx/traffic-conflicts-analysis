import time

from datetime import datetime as Datetime


#Singleton class to avoid multiple DBMS connection pointers/calls
class GenericEntity():

    #Globals cursors
    __globals = None

    #Pointers shared whit childs
    enviroment = {
        '__connection_name': None,
        '__entity': None,
        '__db_manager': None,
    }

    #Database connection associated to entities repository
    __connection_name = None

    #Entity name
    __entity = None

    #Entity fields
    __fields = None

    #DBMS manager pointer
    __db_manager = None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, config, globals ):
        #Globals cursors pointers
        self.__globals = globals
        #Setting the configuration vars
        self.__connection_name = config['connection_name']
        self.__entity = config['entity']
        self.__fields = (
            (
                self.__globals['__global_procedures'].mergeDicts(
                    (
                        {
                            'id': {
                                'name': 'id',
                                'pkey': True,
                            }
                        }
                    ),
                    config['fields']
                )
            ) if (
                config['fields'] and bool( config['fields'] )
            ) else (
                None
            )
        )        
        #Getting the system db manager
        self.__db_manager = self.__globals['__db']['__manager']
        #Settingpointers shared whit childs 
        self.enviroment = {
            '__connection_name': self.__connection_name,
            '__entity': self.__entity,
            '__db_manager': self.__db_manager,
        }
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
        #Error
        if style == 'error':
            if type == 'import_dir':
                self.__globals['__log'].setLog(
                    (
                        '---------------------------------------\n' +
                        'El directorio de importacion no existe:\n' +
                        '---------------------------------------\n' +
                        'En la conexion [' + connection_name + '].\n' +
                        message_for 
                    ),
                    code = 404,
                    type = 'error'
                )
        #Notices
        elif style == 'notice':
            if type == 'entity_imported':
                self.__globals['__log'].setLog(
                    (
                        '---------------------------------------------------\n' +
                        'Importando datos CSV a la entidad de base de datos:\n' +
                        '---------------------------------------------------\n' +
                        'La entidad ' + message_for + '. \n' +
                        'Este proceso ha finalizado en la conexion: [' + connection_name + '].' 
                    )
                )
            elif type == 'imported_file_renamed':    
                self.__globals['__log'].setLog(
                    (
                        '-------------------------------------------\n' +
                        'Archivo importado RENOMBRADO en directorio:\n' +
                        '-------------------------------------------\n' +
                        message_for + 
                        'Este proceso ha finalizado en la conexion: [' + connection_name + '].' 
                    )
                )
        #Nothing go back
        return None   

    #-----------------------------------------------------------------------------------------------------------------------------
    def __buildDataAutoImport( self, converters ):
        """
        Builds the entity data auto import
        Returns:
            [None]: None
        """
        #Auto import directory
        auto_import_path = (
            [
                'Public',
                'db_default',
                'auto_import',
                self.__entity
            ]
        )
        #Scanning auto-import data  
        scans = self.__globals['__global_procedures'].scanSingleDirectory( auto_import_path )
        #Invalid scan?
        if scans is None:
            self.__logMessage(
                'error', 
                'import_dir',
                self.__connection_name,
                (
                    'El directorio de auto-importacion [' + self.__entity + '] no existe. \n' +
                    'Ninguna importacion fue generada por [Entity.__buildDataAutoImport]'
                )
            )
            return None        
        #Walking all files
        for files in scans['_files']:
            #Unimported file?
            if (
                files['_name'].startswith( self.__entity + '__branch_' ) and
                files['_name'].endswith( '.csv' )
            ):
                #3) Setting the collected Panda
                self.__db_manager.savePandaToDb(
                    self.__connection_name,
                    self.__entity,
                    #2) Personalizing auto importation from entity mods
                    self.personalizeCsvAutoImport(
                        #1) Collecting Panda from CSV file
                        self.__db_manager.getPandaCsv(
                            files['_name'],
                            auto_import_path,
                            converters = converters
                        )
                    )
                )
                #Loggin the importation
                self.__logMessage( 
                    'notice', 
                    'entity_imported', 
                    self.__connection_name, 
                    '[' + self.__entity + '] ha importado registris del archivo: [' + files['_name'] + ']'
                )
                #New file name
                new_name = files['_name'] + '.__imported_at__' + Datetime.today().strftime( '%Y_%m_%d-%H_%M_%S' ) + '__.done'
                #Renamimg imported CSV
                self.__globals['__global_procedures'].renameFile(
                    #Old name
                    ( auto_import_path + [ files['_name'] ] ),
                    #New name
                    ( auto_import_path + [ 'imported', new_name ] )
                )
                #Loggin the rename
                self.__logMessage( 
                    'notice', 
                    'imported_file_renamed', 
                    self.__connection_name, 
                    '[' + files['_name'] + '] ha sido movido al directorio [imported] y renombrado como [' + new_name + ']'
                )
                #Sleep one second to avoid files with same name impacts
                time.sleep( 1 )
        #Query results go back!
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def personalizeCsvAutoImport( self, panda_csv ):
        """
        Personalize the CSV auto importation Panda object
        Returns:
            [panda]: The formatted Panda object
        """
        return panda_csv

    #-----------------------------------------------------------------------------------------------------------------------------
    def getEntityName( self ):
        """
        Returns the entity name
        Returns:
            [string]: Entity name
        """
        return self.__entity

    #-----------------------------------------------------------------------------------------------------------------------------
    def _getFields( self, with_primary_keys = False ):
        """
        Gets the fields information and return that info
            with_primary_keys ([bool]): Returns the primary key fields
        Returns:
            [dict]: Fields info
        """        
        if with_primary_keys:
            #Full go back
            return self.__fields
        #Get with no keys
        fields = {}
        #Walking fields
        for field in self.__fields:
            #Avoid primary keys
            if (
                'pkey' not in self.__fields[field] or
                       not self.__fields[field]['pkey']
            ):
                fields[field] = self.__fields[field]
        #Simplified go back
        return fields

    #-----------------------------------------------------------------------------------------------------------------------------
    def _buildEntity( self, auto_import = False, converters = None ):
        """
        Builds the system database entity
        Args:
            auto_import ([string]): Plays an auto importation of data, if applies for this entity
            converters ([mapping]): Panda converters
        Returns:
            [None]: None
        """
        #Builder db execution
        self.__db_manager.buildEntity(
            #Database connection that will set the entity inside
            self.__connection_name,
            self.__entity, 
            self._getFields( True )
        )
        #Now playing the auto importation
        if auto_import:
            self.__buildDataAutoImport( converters )
        #Now, playing the SQL executions after entity is builded
        self.executeDefaultSqlAfterEntityBuilded()
        #Query results go back!
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def _buildSingleEntity( self, entity_name, fields, auto_import = False, converters = None ):
        """
        Builds the system database entity
        Args:
            entity_name ([string]): The name of the db entity (table) to build in the specified connection
            fields ([dict]): Collection of fields configurations to set in db
            auto_import ([string]): Plays an auto importation of data, if applies for this entity
            converters ([mapping]): Panda converters
        Returns:
            [None]: None
        """
        if (
            ( entity_name ) and
            ( type( fields ) is dict ) and
            ( bool( fields ) )
        ):
            #Builder db execution
            self.__db_manager.buildEntity(
                #Database connection that will set the entity inside
                self.__connection_name,
                entity_name, 
                self.__globals['__global_procedures'].mergeDicts(
                    {
                        'id': {
                            'name': 'id',
                            'type': 'INT',
                            'pkey': True,
                        },
                    },
                    fields
                ),
            )
            #Now playing the auto importation
            if auto_import:
                self.__buildDataAutoImport( converters )
            #Now, playing the SQL executions after entity is builded
            self.executeDefaultSqlAfterEntityBuilded()
        #Query results go back!
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def _getEntityDataDump( self ):
        """
        Returns the entity data dump
        Returns:
            [None]: None
        """
        #Query results go back!
        return (
            self.__db_manager.getFullEntity(
                self.__connection_name, 
                self.__entity, 
                self._getFields(), 
                'panda' 
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    def insert( self, datarows ):
        """
        Inserts records for this entity
        Args:
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
        return (
            self.__db_manager.insert(
                self.__connection_name, 
                self.__entity, 
                datarows
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    def executeDefaultSqlAfterEntityBuilded( self, ):
        """
        Executes the default SQL after the entity is builded
        Returns:
            [None]: None
        """
        #Getting default SQL
        default_sql = self.getDefaultSqlAfterEntityBuilded()
        #Walking entries
        for sql in default_sql:
            try:
                self.__db_manager.executeQueryFor( self.__connection_name, sql )
            except:
                pass

    #-----------------------------------------------------------------------------------------------------------------------------
    def getDefaultSqlAfterEntityBuilded( self, ):
        """
        Returns the default SQL to execute when the entity is alredy builded
        Returns:
            [list]: List of sql entries to execute
        """
        return []

    #-----------------------------------------------------------------------------------------------------------------------------
    def pandaSetMailerPandaHeadersWhileSavingCsv( self, item ):
        """
        Panda headers settings for mailer attachment
        Args:
            item ([dict]): The full attachment item
        Returns:
            [dict]: Columns to modify at mailer time
        """
        #Empty mods go back
        return {}

    #-----------------------------------------------------------------------------------------------------------------------------
    def pandaFinalPandaFieldsCheckBeforeSavingCsv( self, panda, status_key ):
        """
        Panda headers settings for mailer attachment
        Args:
            panda ([panda]): Panda dataset to evaluate
            status_key ([string]): Status value in a key form
        Returns:
            [panda]: The formatted item sent
        """
        #Item go back
        return panda

    #-----------------------------------------------------------------------------------------------------------------------------
    def pandaSetsBeforeSaveCsv( self, items ):
        """
        Final panda settings before save his data
        Args:
            items ([list]): List of dictionaries with Pandas information
                            Example:
                            [
                                ...,
                                {
                                    'panda_obj': some_panda_obj,                 #Panda dataset object to play with his info
                                    'attach_csv_to_email': True,                 #Boolean that attach this Panda CSV to email
                                    'attach_csv_file_alias': 'CSVFileNameAlias', #Name that will be the main alias filename
                                    'save_on_entity': True,                      #Boolean that saves the Panda to the entity
                                },
                                ...,
                            ]
        Returns:
            [None]: None
        """
        #Saviors repository
        saviors = []
        #Attachments repository
        attachments = []
        #Walking saves
        for key in items:
            item = items[key]
            #Items to be db-saved
            if item['save_on_entity']:
                #Files attachment mode to email
                mail_files_attachment_mode = self.__globals['__config'].get( 'release_info' )['mail_files_attachment_mode']
                #Appending savior
                saviors.append(
                    {
                        'panda': (
                            (
                                item['panda_obj']
                            ) if (
                                #Only when the mailer files must be added in one 
                                mail_files_attachment_mode == 'one_per_conciliation'
                            ) else (
                                self.pandaFinalPandaFieldsCheckBeforeSavingCsv( 
                                    item['panda_obj'], 
                                    key
                                ) 
                            )
                        ),
                    }
                )
            #Appending the email attachment if applies
            if item['attach_csv_to_email']:
                attachments.append(
                    {
                        'panda': item['panda_obj'],
                        'panda_column_renames': self.pandaSetMailerPandaHeadersWhileSavingCsv( item ),
                        'panda_column_actives': (
                            (
                                item['csv_columns']
                            ) if (
                                'csv_columns' in item
                            ) else (
                                None
                            )
                        ),
                        'csv_base_name': item['attach_csv_file_alias'] + '_' + str( key ),
                        'csv_separator': item['csv_separator'],
                        'csv_encoding': item['csv_encoding'],
                        'csv_max_rows': item['csv_max_rows'],
                    }
                )
        #Configs go back
        return {
            'saviors': saviors,
            'attachments': attachments,
        }

    #-----------------------------------------------------------------------------------------------------------------------------
    def saveEntityByPanda( self, items, ):
        """
        Saves the entity with a list of Pandas objects
        Args:
            items ([list]): List of dictionaries with Pandas information
                            Example:
                            [
                                ...,
                                {
                                    'panda_obj': some_panda_obj,                 #Panda dataset object to play with his info
                                    'attach_csv_to_email': True,                 #Boolean that attach this Panda CSV to email
                                    'attach_csv_file_alias': 'CSVFileNameAlias', #Name that will be the main alias filename
                                    'save_on_entity': True,                      #Boolean that saves the Panda to the entity
                                },
                                ...,
                            ]
            send_mail ([bool]): Able/Disable the mail sender procedure
        Returns:
            [None]: None
        """
        #Setting last saves updates by reference and getting the "sets" for CSVs and email procedures
        sets = self.pandaSetsBeforeSaveCsv( items )
        #Walking saves
        for savior in sets['saviors']:
            #Saving procedure
            self.__db_manager.savePandaToDb(
                self.__connection_name, 
                self.__entity, 
                savior['panda']
            )
        #Attachments go back
        return sets['attachments']
