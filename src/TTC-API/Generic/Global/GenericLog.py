import pprint

#Local imports
from Generic.Global.Borg import Borg

#Mainn log class
class GenericLog( Borg ):

    #Global objects pointers
    __globals = None

    #Global run id
    __global_run_id = None

    #Datetime for this instance on singleton logic
    __singleton_datetime = None

    #Datetime for this instance on singleton logic
    __singleton_log_file_route = None

    #Log text repository to save on conciliation run
    __log_text = ''

    #Config
    __config = None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the configurations are made just once (singleton class)
        Returns:
            [None]: None
        """
        #Global objects pointers retriving
        self.__globals = globals
        #Global run id assignation
        self.__global_run_id = self.__globals['__global_procedures'].getUniqueGenericId( type = 'int', sleep = 100 )
        #Saving the configuration info
        self.__config = self.__globals['__config'].get( 'log_resource' )
        #Building automatic log folders
        self.__createAutoLogRepos()
        #Singleton datetime for this instance
        self.__singleton_datetime = self.__globals['__global_procedures'].getTodayString( mask = '___%Y_%m_%d__%H_%M_%S' )
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __createAutoLogRepos( self, ):
        """
        Make the automatic log repos if doesn exists
        Returns:
            [None]: None
        """
        #Global procedures pointer
        __global_procedures = self.__globals['__global_procedures']
        #Full base path string
        full_base_path = __global_procedures.getDirectoryCleanPath( self.__config['path'], make_if_not_exists = True )
        #Making related subpaths if applies
        for key in ( 'log', 'dbg' ):
            #Item prefix
            prefix = (
                __global_procedures.getDirectoryCleanPath(
                    self.__config[key + '_subpath_and_file_prefix' ], 
                    include_base_path = False 
                )
            )
            #Prefix has subpath?
            if '/' in prefix:
                #Item folder build try
                __global_procedures.getDirectoryCleanPath(
                    (
                        full_base_path + 
                        '/' +
                        #Item path without file prefix
                        prefix.rsplit( '/', 1 )[0]
                    ),
                    make_if_not_exists = True,
                    include_base_path = False
                )
        #Nope go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __getInstanceGlobalLogFileRoute( self, full_path = False ):
        """
        Gets the global instance log file name
        """
        #File name setted?  
        if self.__singleton_log_file_route is None:
            #Getting path sections
            paths = (
                self.__config['path'] + '/' +
                self.__config['log_subpath_and_file_prefix'] + 
                self.__singleton_datetime +
                '.log'
            ).replace(
                '\\',
                '/'
            ).split( 
                '/' 
            )
            #Final singleton log path routes
            self.__singleton_log_file_route = {
                'file_name': paths[-1],
                'file_path': self.__globals['__global_procedures'].joinPath( paths ),
            }
        #Route go back
        return self.__singleton_log_file_route

    #-----------------------------------------------------------------------------------------------------------------------------
    def __setFileEntry( self, file, message, path = None, mode = 1, is_log = True, check_abled_on_config = False ):
        """
        Sets/Adds an entry in the file sent
        Args:
            file ([string]): File name to store the log
            message ([string]): Log information/message
            path ([list]): Directories of the file path, one item per path directory
            mode ([int]): 1 (Add to file bottom), 2 (Remove all content and set the new one)
            is_log ([bool]): Identifies if the entry is for a log system file
            check_abled_on_config ([bool]): Checks if the configuration is abled to set logs:
                                            - On True: Sets the log if the config['abled'] is 1 (abled)
                                            - On False: Sets the log anyhow
        Returns:
            [None]: None
        """
        #If logs are disabled, go back with None!
        if (
            check_abled_on_config and
            str( self.__config['abled'] ) == '0'
        ):
            return None
        #Configurated path retrival
        if path is None:
            path = self.__config['path'].split( '/' )
        #Configurated path retrival
        if file is None:
            file = (
                self.__config['log_subpath_and_file_prefix'] + 
                self.__singleton_datetime +
                '.log'
            ).replace(
                '\\',
                '/'
            )
        #File open mode
        open_mode = ( 'w' if mode == 2 else 'a' ) # 'r+' ?
        #Open log
        file = (
            open(
                self.__globals['__global_procedures'].joinPath(
                    path + (
                        #File has subfolders?
                        (
                            file.split( '/' )
                        ) if (
                            '/' in file
                        ) else (
                            [ file ]
                        )
                    )
                ), 
                open_mode 
            )
        )
        #Saving record
        file.writelines(
            [
                message, 
                ( "\n---------------\n" if is_log else '' )
            ]
        )
        #Closing pointer
        file.close()
        #Nope go back!
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __cleanLogFiles( self, ):
        #Getting the max files
        try:
            max_files = int( self.__config['max_files'] )
        except:
            #Max files error
            self.setLog( 
                'No se borraron logs. La variable [max_files] = [' + self.__config['max_files'] + '] no es un valor entero' 
            )
            #Nope go back
            return None
        #Max files is 0 or smaller?
        if max_files < 1:
            return None
        else:
            self.setLog(
                'Se preservaran maximo: [' + self.__config['max_files'] + '] archivos .log'
            )
        #Folder pieces
        pfix_pieces = []
        path_pieces = []
        #The log prefix has folder path?
        if self.__config['log_subpath_and_file_prefix']:
            pfx = str( self.__config['log_subpath_and_file_prefix'] ).replace( '\\', '/' )
            #Has subfolder assigned?
            if '/' in pfx:
                pfix_pieces = pfx.split( '/' )[:-1]
        #Log path pieces
        if self.__config['path']:
            path = str( self.__config['path'] ).replace( '\\', '/' )
            #Has folders path?
            if '/' in path:
                path_pieces += path.split( '/' )
            else:
                path_pieces.append( path )
        #Final super path
        super_pieces = path_pieces + pfix_pieces
        #Files to play
        files = []
        #Getting scanned folder
        contents = self.__globals['__global_procedures'].scanSingleDirectory( super_pieces )
        #Walking files in contents
        for file in contents['_files']:
            files.append( file['_name'] )
        #Sorting the collected logs
        files.sort( reverse = True )
        #Items to delete
        unlink_items = []
        #Walking ordered files
        for idx, filename in enumerate( files ):
            if idx > max_files:
                unlink_items.append( super_pieces + [ filename ] )
        #Executing final unlink procedure
        self.__globals['__global_procedures'].removeFiles( unlink_items )
        #Unlink log
        self.setLog( 
            'Se eliminaron los siguientes archivos log: ' + ( str( unlink_items ) if len( unlink_items ) else 'NINGUNO' )
        )
        #Nope go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    #---------------------------------------------------- Public methods ---------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------------------------------------------------
    def getGlobalRunId( self, ):
        return self.__global_run_id

    #-----------------------------------------------------------------------------------------------------------------------------
    def cleanLogFiles( self, ):
        self.__cleanLogFiles()

    #-----------------------------------------------------------------------------------------------------------------------------
    def getInstanceGlobalLogFileRoute( self, ):
        """
        Gets the global instance log file name
        Returns:
            [(string)]: Global log file name
        """
        return self.__getInstanceGlobalLogFileRoute()

    #-----------------------------------------------------------------------------------------------------------------------------
    def setFreeFile( self, file_name, file_path, content, mode = 1 ):
        """
        Sets a string-content in the file and path sent
        Args:
            file_name ([string]): File name (with extension) to store the content
            file_path ([string]): Directories of the file path, one item per path directory, in order of deep!
            content ([string]): String file content
            mode ([string]): 1 (Add to file bottom), 2 (Remove all content and set the new one)
        Returns:
            [None]: None
        """
        self.__setFileEntry( file_name, content, file_path, mode, False )
        #Nope go back!
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def setDebug( self, variable, file_name = None, one_file_to_all = True ):
        """
        Sets/Adds a debug entry in the [movistar_conciliation_debug_log.log] debug log
        Args:
            variable ([mixed]): Data to [debug]
            file_name ([string]): Name of the file to build
            one_file_to_all ([bool]): Flag to set one file per debug sent
        Returns:
            [None]: None
        """
        self.__setFileEntry(
            (
                (
                    (
                        str( self.__globals['__config'].get( 'log_resource' )['dbg_subpath_and_file_prefix'] ) + '.log'
                    ) if (
                        one_file_to_all
                    ) else (
                        self.__globals['__global_procedures'].getUniqueGenericId(
                            prefix = (
                                str(
                                    self.__globals['__config'].get( 'log_resource' )['dbg_subpath_and_file_prefix'] 
                                ) + 
                                self.__singleton_datetime +
                                '___'
                            )
                        ) + '.log'
                    )
                ) if (
                    file_name is None 
                ) else (
                    file_name
                )
            ),
            (
                '[' + self.__globals['__global_procedures'].getUniqueGenericId( 'DEBUG-' ) + ']' +
                "\n\n" +
                pprint.pformat( variable, indent = 4 ) +
                "\n"
            )
        )
        #Nope go back!
        return None
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def setLog( self, message, code = 200, type = 'notice', datetime = 'default', print_on_console = True ):
        """
        Sets a string-content in the file and path sent
        Args:
            message ([string]): Text to be log
            code ([int]): 200, 404 o 500
            type ([string]): [notice], [error], [warning] or [exception]
            datetime ([string]): Datetime string to set
        Returns:
            [None]: None
        """
        #Fixing today string
        today_str = '[' + ( self.__globals['__global_procedures'].getTodayString() if datetime == 'default' else datetime ) + ']'
        #Setting the type
        if type == 'notice':
            log_text = today_str + '[INFO][' + str( code ) + ']:'
        elif type == 'warning':
            log_text = today_str + '[WARN][' + str( code ) + ']:'
        elif type == 'error':
            log_text = today_str + '[ERROR][' + str( code ) + ']:'
        elif type == 'exception':
            log_text = today_str + '[EXCEPTION][' + str( code ) + ']:'
        else:
            log_text = None
        #A valid message?
        if not ( log_text is None ):
            #Log text
            log_text = (
                '---------------------------------\n' +
                log_text +
                message + '\n'
            )
            #Saving the global log text to conciliation run saves
            self.__log_text += ( '' if self.__log_text == '' else '<<item>>' ) + log_text
            #Log set
            self.__setFileEntry( None, log_text, check_abled_on_config = True, is_log = False )
            #Also on console?
            if print_on_console and ( str( self.__globals['__config'].get( 'log_resource' )['print_on_console'] ) == '1' ):
                print( log_text )
        #Nope go back!
        return None
