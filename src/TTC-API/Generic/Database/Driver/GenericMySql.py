import time

#Singleton class to avoid multiple DBMS connection pointers/calls
class GenericMySql( ):

    #Globals cursors
    __globals = None

    #Global FKs collection
    __all_sql_system_auto_fkeys = []

    #Max entity definitions chars in names
    __max_chars_in_definitions = 58

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        #Globals cursors pointers
        self.__globals = globals
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __createEntity( self, entity_name, fields ):
        """
        Creates an entity SQL builder code, and tries to set that into a database
        Returns:
            [string]: SQL string creation code
        """
        #Base vars
        primary = []
        sql_entity_fields_builder_code = ''
        sql_system_auto_maker = []
        sql_system_auto_pkeys = ''
        sql_system_auto_fkeys = []
        sql_system_auto_index = []
        sql_system_auto_fk = None
        sql_system_create_table_fk = ''
        sql_system_create_table_index = ''
        #Walking fields setted
        for field in fields:
            #Field item pointer
            item = fields[field]
            #Foreing key flag set
            is_fk = self.isManyToOneFkField( field )
            #Checking if field is a foreing key
            if is_fk:
                #Fk field name
                field_name = self.getMany2OneFkFieldName( field, item )
                #Default fk field type?
                if not ( 'type' in item ):
                    item['type'] = 'BIGINT'
                #Foreing data
                fk_entity_name = item['entity_model']().getEntityName()
                fk_field = ( item['related_model_id_field'] if ( 'related_model_id_field' in item ) else 'id' )
                fk_constraint = (
                    self.__globals['__global_procedures'].getMD5Hash( 
                        ( entity_name + field_name + fk_entity_name + fk_field )
                    ) + 
                    '_' + 
                    field.replace( '__m2o_', '' )
                )
                #Truncate if max 64 chars is reached to fk constraint name
                if len( fk_constraint ) > self.__max_chars_in_definitions:
                    fk_constraint = fk_constraint[0:self.__max_chars_in_definitions]
                #Foreing key SQLs
                sql_system_auto_fk = (
                    'ALTER TABLE ' + entity_name + ' ' +
                    'ADD CONSTRAINT FK_' + fk_constraint + ' ' +
                    'FOREIGN KEY ( ' + field_name + ' ) REFERENCES ' + fk_entity_name + '( ' + fk_field + ' );'
                )
                sql_system_create_table_fk += (
                    '  CONSTRAINT FK_' + fk_constraint + ' FOREIGN KEY ( ' + field_name + ' )' + "\n" 
                    '  REFERENCES ' + fk_entity_name + '( ' + fk_field + ' )' + "\n"
                )
            else:
                #Regular field name
                field_name = field
                #Foreing key is False
                sql_system_auto_fk = False
            #Field name max len reached?
            if len( field_name ) > 64:
                raise (
                    Exception( 
                        'GenericMySql.__createEntity: DbEntity Field-Name [' + field_name + '] is too long. 64 chars max' 
                    )
                )
            #The field is a primary key? and no foreing key...
            if not is_fk and ( 'pkey' in item ):
                primary.append( field_name )
                sql_system_auto_pkeys += ( '  ' + field_name + ' BIGINT NOT NULL AUTO_INCREMENT,' + "\n" )
            #No?, setting the field SQL string code then...
            else:
                #Default and/or null?
                default = ( ' DEFAULT ' + item['default'] if ( 'default' in item ) else '' )
                nullstr = ( ' NOT NULL ' if ( ( 'not_null' in item ) and item['not_null'] ) else '' )
                #Auto field maker SQL
                sql_system_auto_maker.append(
                    'ALTER TABLE ' + entity_name + ' ADD ' + field_name + ' ' + item['type'] + nullstr + default + ';'
                )
                #Auto index?
                if ( 'index' in item ) and item['index']:
                    #Auto section
                    sql_system_auto_index.append(
                        #'ALTER TABLE ' + entity_name + ' ADD INDEX ' + field_name + ' ( ' + field_name + ' );'
                        'CREATE INDEX ' + field_name + ' ON ' + entity_name + ' ( ' + field_name + ' );'
                    )
                    #Create table string
                    sql_system_create_table_index += (
                        ( ',' if sql_system_create_table_index else '' ) + 
                        "\n" + 
                        '  INDEX ' + field_name + ' ( ' + field_name + ' )' 
                    )
                #Auto foreing key maker SQL
                if sql_system_auto_fk:
                    sql_system_auto_fkeys.append( sql_system_auto_fk )
                #String on file savior SQL
                sql_entity_fields_builder_code += ( '  ' + field_name + ' ' + item['type'] + default + ',' + "\n" )        
        #System main entity structure
        sql_create_table = (
            'CREATE TABLE IF NOT EXISTS ' + entity_name + ' (' + "\n" +
                sql_system_auto_pkeys +
                '__REPLACE_FOR_FIELDS__' +
                (
                    (
                        (
                            '  CONSTRAINT PK_' + self.__pkConstraintName( entity_name ) +
                            '  PRIMARY KEY ( ' + ( ',' ).join( primary ) + ' )'
                        )
                        if (
                            len( primary ) > 1
                        ) 
                        else (
                            '  PRIMARY KEY ( ' + str( primary[0] ) + ' )'
                        )
                    )
                ) +
                '__REPLACE_FOR_INDEX__' +
                '__REPLACE_FOR_FK__' +
            ');'
        )
        #Saving the mysql entity creator on a sql code file
        self.__globals['__log'].setFreeFile(
             entity_name + '_mysql_create.sql',
            [ 'Public', 'scripts' ],
            (
                sql_create_table.replace(
                    '__REPLACE_FOR_FIELDS__',
                    sql_entity_fields_builder_code
                ).replace(
                    '__REPLACE_FOR_INDEX__',
                    (
                        (
                            ',' + sql_system_create_table_index
                        ) if (
                            sql_system_create_table_index
                        ) else (
                            ''
                        )
                    )
                ).replace(
                    '__REPLACE_FOR_FK__',
                    (
                        ( 
                            ',' + "\n" if sql_system_create_table_fk else '' 
                        ) +
                        sql_system_create_table_fk +
                        "\n"
                    )
                )
            ),
            2
        )
        #Auto builder info go back!
        return [
            ( 
                [
                    sql_create_table.replace( 
                        '__REPLACE_FOR_FIELDS__', 
                        '' 
                    ).replace( 
                        '__REPLACE_FOR_INDEX__', 
                        '' 
                    ).replace( 
                        '__REPLACE_FOR_FK__', 
                        '' 
                    )
                ] +
                sql_system_auto_maker 
            ), 
            sql_system_auto_fkeys,
            sql_system_auto_index
        ]
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def __pkConstraintName( self, entity_name ):
        #Primary key constraint name
        pk_constraint = self.__globals['__global_procedures'].getUniqueGenericId( sleep = 20 ) + '_' + entity_name
        #Valid pk constraint name?
        if len( pk_constraint ) > self.__max_chars_in_definitions:
            pk_constraint = pk_constraint[0:self.__max_chars_in_definitions]
        #Name go back
        return pk_constraint

    #-----------------------------------------------------------------------------------------------------------------------------
    def isManyToOneFkField( self, item_key ):
        try:
            return item_key.index( '__m2o_' ) == 0
        except:
            pass
        #Nope
        return False

    #-----------------------------------------------------------------------------------------------------------------------------
    def getMany2OneFkFieldName( self, item_key, item ):
        return (
            item_key.replace(
                '__m2o_', 
                (
                    '__m2o_' + 
                    (
                        (
                            str( item['entity_model'].__name__ )
                        ) if (
                            not ( 'model_prefix' in item ) or
                            item['model_prefix']
                        ) else (
                            '' 
                        )
                    ) +
                    '_' 
                )
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    def getFullEntityQuery( self, entity_name, fields, alias_prefix = '' ):
        """
        Builds an entity in a database from the connection sent
        Args:
            entity_name ([string]): Entity name to get full data
            fields ([dict]): List of dictionaries with entity field name/data to get
            alias_prefix ([string]): Alias prefix for the fields sent
        Returns:
            [string]: SQL query full entity
        """
        sql_fields = ''
        #Getting query fields
        for field in fields:
            sql_fields += ( '' if sql_fields == '' else ',' ) + field + ' AS ' + alias_prefix + field
        #Returning the builded SQL query
        return 'SELECT ' + sql_fields + ' FROM '+ entity_name
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def executeEntityBuilder( self, db_connector, entity_name, fields, small_debriefing = True ):
        #Auto makers retrival
        ( 
            sql_system_auto_maker, 
            sql_system_auto_fkeys,
            sql_system_auto_index
        ) = (
            self.__createEntity( entity_name, fields )
        )
        #Adding FKs to global collection
        self.__all_sql_system_auto_fkeys.append(
            {
                'db_connector': db_connector,
                'fks_sql': sql_system_auto_fkeys,
                'entity_name': entity_name,
                #'fields': fields,
            }
        )
        #Super timemark
        super_timemark = time.perf_counter()
        #Full SQL debriefing
        sql_debriefing = ''
        #Auto sections building
        for section in [
            #Fields first
            sql_system_auto_maker, 
            #Indexes second
            sql_system_auto_index
        ]:
            #Walking all SQL sections
            for sql in section:
                #Mark momment
                timemark = time.perf_counter()
                #Trying to play the SQL
                try:
                    db_connector['_cursor'].execute( sql, None )
                    #Clean SQL
                    clean_sql = sql.replace( '\n', '' )
                    #Debrifing ok
                    sql_debriefing += (
                        '\n    SQL: ( ' + clean_sql + ' ) : [Executed OK][' + str( time.perf_counter() - timemark ) + ' sec]'
                    )
                except Exception as e:
                    #Debrifing error
                    sql_debriefing += (
                        '\n    SQL: ( ' + sql + ' ) : [' + str( e ) + '][' + str( time.perf_counter() - timemark ) + ' sec]'
                    )
        #Before commit momment
        timemark = time.perf_counter()
        #Commit changes
        db_connector['_connection'].commit()
        #Final changes commited debrief
        sql_debriefing += '\n    COMMIT CHANGES TIMER: [' + str( time.perf_counter() - timemark ) + ' sec]'
        #Small debriefing?
        if small_debriefing:
            self.__globals['__log'].setLog(
                'Verificacion de entidad (tabla) de Base de Datos [' + str( entity_name ) + ']: ' +
                'Terminada en [' + str( time.perf_counter() - super_timemark ) + '] sec'
            )
        else:
            self.__globals['__log'].setLog(
                'Log de verificacion al crear entidad (tabla) de Base de Datos\n' +
                '****************************************************************************************************\n' +
                'Se intentaron ejecutar estos SQL para creacion de entidad y se obtuvieron los siguientes resultados:\n' +
                '****************************************************************************************************\n' +
                sql_debriefing
            )
        #Goodbye
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def resolveAndBuildAllEntitiesForeingKeys( self, small_debriefing = True ):
        #Super timemark
        super_timemark = time.perf_counter()
        #Debriefing
        sql_debriefing = ''
        #Walking all auto fks collection
        for auto_fkey in self.__all_sql_system_auto_fkeys:
            #Building auto fkey
            for sql in auto_fkey['fks_sql']:
                #SQL log
                sql_debriefing += '\n    SQL [' + auto_fkey['entity_name'] + ']: ( ' + sql
                #Time mark
                timemark = time.perf_counter()
                #SQL execute try
                try:
                    auto_fkey['db_connector']['_cursor'].execute( sql, None )
                    #All ok log
                    sql_debriefing += ' ) : [Executed OK][' + str( time.perf_counter() - timemark ) + ' sec]'
                except Exception as e:
                    #Error log
                    sql_debriefing += ' ) : [' + str( e ) + '][' + str( time.perf_counter() - timemark ) + ' sec]'
        #Time mark over commit changes
        timemark = time.perf_counter()
        #Commit fks changes
        auto_fkey['db_connector']['_connection'].commit()
        #Final debrief over changes committed
        sql_debriefing += '\n    COMMIT CHANGES TIMER: [' + str( time.perf_counter() - timemark ) + ' sec]'
        #Small debriefing?
        if small_debriefing:
            self.__globals['__log'].setLog(
                'Verificacion de FK (llaves foraneas) de Base de Datos [' + str( auto_fkey['entity_name'] ) + ']: ' +
                'Terminada en [' + str( time.perf_counter() - super_timemark ) + '] sec'
            )
        else:
            self.__globals['__log'].setLog(
                'Log de verificacion al crear FK (llaves foraneas) en Base de Datos\n' +
                '*****************************************************************************************************\n' +
                'Se intentaron ejecutar los siguientes SQL de creacion de relaciones FK con los siguientes resultados:\n' +
                '*****************************************************************************************************\n' +
                sql_debriefing
            )
        #Goodbye
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def insert( self, db_connector, entity_name, datarows ):
        """
        Inserts a MySQL records
        Args:
            db_connector ([mixed]): Object to call for execute a connected db procedure
            entity_name ([string]): Db entity/table name to perform
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
        set_fields = True
        sql_fields = ''
        sql_values = ''
        #Walking data rows
        for datarow in datarows:
            sql_values_string = ''
            #Walking fields data
            for field in datarow:
                #Setting fields if applies
                if set_fields:
                    sql_fields += ( '' if sql_fields == '' else ', ' ) + field
                #Setting the values
                string_value = str( datarow[field]['value'] ).replace( "'", r"\'" )
                sql_values_string += (
                    ( '' if sql_values_string == '' else ', ' ) + 
                    (
                        ( 
                            "'" + string_value + "'" 
                        ) if ( 
                            ( 'quote' in datarow[field] ) and ( datarow[field]['quote'] )
                        ) else ( 
                            string_value 
                        )
                    )
                )
            #Values found?
            if sql_values_string != '':
                #Setting values row then
                sql_values += ( '' if sql_values == '' else ', ' ) + '( ' + sql_values_string + ' )'
            #No more headers/fields
            set_fields = False
        #Insertion go ahead
        return (
            self.executeQuery(
                db_connector,  
                (
                    'INSERT INTO ' + entity_name + ' ( ' + sql_fields + ' ) VALUES ' + sql_values
                )
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    def executeQuery( self, db_connector, sql, vars = None ):
        """
        Executes a query for the connector sent
        Args:
            db_connector ([type]): Connector to execute
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
        #Execute...
        result = db_connector['_cursor'].execute( sql, vars )
        #And commit then...
        db_connector['_connection'].commit()
        #Results go back!...
        return result

    #-----------------------------------------------------------------------------------------------------------------------------
    def playQuery( self, db_connector, sql, vars = None ):
        """
        Plays a query for the connector sent
        Args:
            db_connector ([type]): Connector to execute
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
            [iterator]: Iterator with all consulted results
        """
        #Play...
        db_connector['_cursor'].execute( sql, vars )
        #And result-set go back!...
        return db_connector['_cursor'].fetchall()
