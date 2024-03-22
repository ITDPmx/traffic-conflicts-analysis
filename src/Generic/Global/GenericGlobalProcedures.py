from copy import copy
import os
import sys
import time
import random
import importlib
import json
import shutil
import hashlib

from os import scandir
from random import randrange
from datetime import datetime as Datetime, timedelta as Timedelta, date as Date
from dateutil.parser import parse as DatetimeParser

from Generic.Global.Borg import Borg

class GenericGlobalProcedures( Borg ):

    #Private root path
    __root_system_path = None

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getMD5UniqueIntOfValue( value, max_len = None, int_parse = False ):
        """
        Returns a unique integer representing the value sent
        Args:
            value ([string]): The string value to get his integer unique twin
            max_len ([int]): Integer that cuts the string to a [max_len] char length
            int_parse ([bool]): To return an integer value. Otherwise a string is returned
        See:
            https://stackoverflow.com/questions/22974499/generate-id-from-string-in-python
        Returns:
            [mixed]: Unique integer or number string
        """
        #Unique int
        full_unique = str( int( GenericGlobalProcedures.getMD5Hash( value ), 16 ) )
        #Checking for length
        response = full_unique[0:max_len] if max_len else full_unique
        #Checking for length and go back
        return ( int( response ) if int_parse else response )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getMD5Hash( value, only_letters = False, exchange = None, case = None ):
        """
        Returns the MD5 [hexdigest] hash for the value sent
        Args:
            value ([string]): Value to MD5 parse
            only_letters ([bool]): Only letters flag
            exchange ([dict]): Number to letter exchange dictionary. Like: { ..., '2': 'X', '3': 'Y', '4': 'Z', ... }
            case ([string]): Can be: "upper", "lower" or None
        Returns:
            [string]: The MD5 [hexdigest] string value
        """
        hash_value = hashlib.md5( str( value ).encode() ).hexdigest()
        #Only letters?
        if only_letters:
            #Letters exchange
            exchange = { '1': 'I', '2': 'Q', '3': 'U', '4': 'N', '5': 'S', '6': 'G', '7': 'T', '8': 'P', '9': 'J', '0': 'O' }
            #Exchange cicle
            for number in exchange:
                hash_value = hash_value.replace( number, exchange[number] )
        #Hash value go back
        return (
            (
                hash_value.upper()
            ) if (
                case == 'upper'
            ) else (
                (
                    hash_value.lower()
                ) if (
                    case == 'lower'
                ) else (
                    hash_value
                )
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def sleep( miliseconds = 1000 ):
        """
        Sleeps on miliseconds
        Args:
            miliseconds ([int]): Number of miliseconds to sleep
        """
        time.sleep( miliseconds / 1000 )
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getUniqueGenericId( prefix = None, type = 'str', multiplies_by = 1000000, sleep = 10 ):
        """
        Gets a generic system ID
        Args:
            prefix ([string]): Prefix to join with the id. It's ignored if arg [type] = [num]
            type ([string]): Sets the type of the response. Can be string [str], numeric [num] or [int]
            multiplied_by ([int]): Amount to expand the tiny-time ID
        Returns:
            [mixed]: Generic ID or None
        """
        #Take a break :)
        GenericGlobalProcedures.sleep( miliseconds = sleep )
        #An integer response?
        try:
            int( str( GenericGlobalProcedures.getActualTinyTime() ).replace( '.', '' ) )
        except:
            return None
        #Unique go back
        return (
            (
                GenericGlobalProcedures.getActualTinyTime( multiplies_by )
            ) if (
                type == 'num'
            ) else (
                (
                    '' if prefix == None else str( prefix )
                ) + (
                    str( GenericGlobalProcedures.getActualTinyTime( multiplies_by ) ).replace( '.', '' )
                )
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getFileName( file ):
        """
        Returns the file name of a file or string file path
        Args:
            file ([mixed]): FileIO or file path string
        Returns:
            [mixed]: File name string or None
        """
        #A fileio name?
        try:
            return os.path.basename( file.name )
        except:
            pass
        #String path as a final check
        try:
            return os.path.basename( str( file ) )
        except:
            pass
        #Nope, nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def checkForOs( get_name = False ):
        #Getting instant client path by platform
        os_platform = str( sys.platform ).lower()
        #Return the platform?
        if get_name:
            return os_platform
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
        #On linux or Mac OS?
        if 'linux' or 'darwin' in os_platform:
            return 'linux'
        #On windows?
        if 'win' in os_platform:
            return 'win'
        #Other OS?
        return 'other'

    #-----------------------------------------------------------------------------------------------------------------------------
    def getBaseFolderDriveByOs():
        """
        Returns the drive string by OS
        Returns:
            [string]: Drive string by OS
        """
        from System.Global.Config import Config
        #To windows
        if GenericGlobalProcedures.checkForOs() == 'win':
            return Config.get( 'to_windows' )['windows_drive']
        #To any other
        return '/'

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getActualScriptFullBasePath( file ):
        """
        Returns the base path of the script that calls this method
        @source: https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
        Args:
            file ([list]): Value of the __file__ var. 
                           Example of this call: 
                                GenericGlobalProcedures.getActualScriptFullBasePath( __file__ )
        Returns:
            [string]: Root/Base system path to script
        """
        return os.path.dirname( os.path.abspath( file ) )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getBaseSystemPath():
        """
        Returns the base path of this system!
        @source: https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
        Returns:
            [string]: Root/Base system path
        """
        if GenericGlobalProcedures.__root_system_path == None:
            GenericGlobalProcedures.__root_system_path = os.path.abspath( os.getcwd() )
        #Base path go back!
        return GenericGlobalProcedures.__root_system_path

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def joinPath( path_pieces, include_base_path = True ):
        """
        Joins the path pieces sent, to prevent SO Windows/Linux path separator compatibilities
        Args:
            path_pieces ([list]): Paths to be joined
            include_base_path ([bool]): Adds the base path to the joined path pieces
        Returns:
            [string]: Joined path
        """
        _path_pieces = [] + path_pieces
        if include_base_path:
            _path_pieces.insert( 0, GenericGlobalProcedures.getBaseSystemPath() )
        #Builded path go back!
        return os.path.join( *_path_pieces )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def scanSingleDirectory( path_pieces, base_path_mode = 1, recursive = False ):
        """
        Scans a single directory specified on the path pieces
        Args:
            path_pieces ([list]): Paths to be joined
            base_path_mode ([int]): Modes to "root" the path pieces sent:
                                        1: Include the base-app-path (/path/to/app/base/folder)
                                        2: Not include any path, just play a relative path-pieces folder
                                        3: Starts the path from OS root folder
            recursive ([recursive]): Scans the path recursively, per a valid directory found inside beyond path-pieces
        Returns:
            [dict|None]: A dictionary with all scanned data | None when the path_pieces are an invalid path
        """        
        #Scans savior
        scans = {
            '_files': [],
            '_directories': [],
        }
        #Base path
        base_path = GenericGlobalProcedures.joinPath(
            (
                (
                    (
                        [ '/' ] 
                    ) if ( 
                        base_path_mode == 3 and 
                        path_pieces[0] != '/' and
                        path_pieces[0] != '\\'
                    ) else (
                        []
                    )
                ) +
                path_pieces
            ), 
            include_base_path = ( base_path_mode == 1 ) 
        )
        #Path exists?
        if os.path.isdir( base_path ):
            #Walking directory
            for scan in scandir( base_path ):
                #Not system or hidden
                if (
                    not scan.name.startswith( '.' ) and
                    not scan.name == '__pycache__'
                ): 
                    item = {
                        '_name': scan.name,
                        '_obj': scan
                    }
                    #Is a file?
                    if scan.is_file():
                        #Appending the file item
                        scans['_files'].append( item )
                    #No?, directory then
                    else:
                        #This item could be recursive 
                        if recursive:
                            item['_contents'] = (
                                GenericGlobalProcedures.scanSingleDirectory(
                                    path_pieces + [ scan.name ],
                                    recursive
                                )
                            )
                        #Appending the final directory item
                        scans['_directories'].append( item )
        #Invalid base path?
        else:
            return None
        #Full tree go back
        return scans

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getDirectoryCleanPath( base, make_if_not_exists = False, include_base_path = True, relative = False ):
        """
        Tries to build the directory path sent
        Args:
            base ([mixed]): String or List of pieces of the path that will be tried to build
            include_base_path ([bool]): Adds the base path to the joined path pieces
        Returns:
            [string]: The full path that was tried to be builded
        """
        os_name = GenericGlobalProcedures.checkForOs()
        #Getting list of pieces from base argument
        if isinstance( base, ( list, ) ):
            base_pieces = base
        else:
            #Cleaning base path sent
            clean_base = (
                (
                    base.replace( '\\', '/' ).replace( '//', '/' )
                ) if (
                    base 
                ) else (
                    ''
                )
            )
            #Is windows?
            if (
                os_name == 'win' and
                ':' in clean_base
            ):
                clean_base = clean_base.replace( ':', ':\\\\' )
            #Getting base pieces
            base_pieces = (
                (
                    ( [] if include_base_path else [ '/' ] )
                ) if (
                    clean_base == '/'
                ) else (
                    (
                        clean_base.split( '/' ) 
                    ) if (
                        clean_base and ( '/' in clean_base )
                    ) else (
                        ( [ clean_base ] if clean_base else [] )
                    )
                )
            )
        #Full base path string
        dir_path = GenericGlobalProcedures.joinPath( base_pieces, include_base_path = include_base_path )
        #Last check for relative path
        if not relative and dir_path and dir_path[0] != '/' and os_name != 'win':
            dir_path = '/' + dir_path
        #Building base path check
        if make_if_not_exists and len( base_pieces ) > 0:
            if not os.path.exists( dir_path ):
                os.mkdir( dir_path )
        #Nope go back
        return dir_path

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def renameFile( old_name, new_name ):
        """
        Renames a file
        Args:
            old_name ([string]): Old file Path/Name
            new_name ([string]): New file Path/Name
        Returns:
            [None]: None
        """
        return (
            os.rename( 
                GenericGlobalProcedures.joinPath( old_name ), 
                GenericGlobalProcedures.joinPath( new_name ) 
            )
        )
    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def createDirectory( dir: list = '',
                         base: str = ''
                       ) -> None:
        
        """
        create a directory
        Args:
            base ([mixed]): str or list base path
            dir ([mixed]): str or list path to create in base path
        Returns:
            [None]: None
        """
        #construct path and clean it
        base = GenericGlobalProcedures.getDirectoryCleanPath(base)
        dir = GenericGlobalProcedures.getDirectoryCleanPath(dir, include_base_path = False)
        try:
            os.makedirs(base + dir)
        except FileExistsError:
            # directory already exists
            pass
        #bye
        return base + dir + '/'

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def removeFiles( unlink_items, base_path_mode = 1 ):
        """
        Delete list items paths sent
        Args:
            unlink_items ([list]): List of list path pieces
            base_path_mode ([int]): Modes to "root" the path pieces sent:
                                        1: Include the base-app-path (/path/to/app/base/folder)
                                        2: Not include any path, just play a relative path-pieces folder
                                        3: Starts the path from OS root folder
        Returns:
            [None]: None
        """
        #Walking items pieces
        for unlink_pieces in unlink_items:
            #Pieces goodbye
            os.unlink(
                GenericGlobalProcedures.joinPath(
                    (
                        (
                            (
                                [ '/' ] 
                            ) if ( 
                                base_path_mode == 3 and 
                                unlink_pieces[0] != '/' and
                                unlink_pieces[0] != '\\'
                            ) else (
                                []
                            )
                        ) +
                        unlink_pieces
                    ), 
                    include_base_path = ( base_path_mode == 1 ) 
                ) 
            )
        #Nope go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def setFileBackup(
        file_name, file_path, destiny_full_base_path, destiny_base_forced_path, datetime = None, os_perms = None, bkup_style = 1
    ):
        """
        Sets a file backup by copying or moving the backuped file sent
        Args:
            file_name (_type_): Actual file name
            file_path (_type_): Actual full file path (without the file name)
            destiny_full_base_path (_type_): This path must exist pr the process will break
            destiny_base_forced_path (_type_): Forced path. If this dont exists, a directory creation will be tryed
            datetime (_type_, optional): Datetime to prefix the new file. None will play de today() dt. False do no set anything
            os_perms ([mixed]): OS permissions for the new file
            bkup_style ([int]): 1 = Move the file, 2 = Make a copy of the file
        Returns:
            [dict]: Dictionary with the process status infos
        """
        #-------------------------
        def getUniqueFilePath( file_path, mask = '%__CNTR__%', counter = 1 ):
            """
            Recursive unique file path/name generator
            Args:
                file_path ([string]): Path string to eval
                mask ([string]): Mask in the [file_path] that will be replaced for the counter try
                counter ([int]): Counter to start the checking/evaluation
            Returns:
                [string]: A unique unexisting file path/name
            """
            #Getting mask value
            mask_value = ( '00' if counter < 10 else ( '0' if counter < 100 else '' ) ) + str( counter )
            #New unique path
            unique_route = file_path.replace( mask, mask_value )
            #Path exists?
            if os.path.exists( unique_route ):
                return getUniqueFilePath( file_path, mask = mask, counter = counter + 1 )
            #Path is new?
            return unique_route
        #-------------------------
        #Clean file paths
        file_path_cls = str( file_path ).replace( '\\', '/' )
        base_path_cls = str( destiny_full_base_path ).replace( '\\', '/' )
        forced_path_cls = str( destiny_base_forced_path ).replace( '\\', '/' )
        #Path collection
        path = {
            #Getting the actual file full path
            'actual': (
                GenericGlobalProcedures.joinPath(
                    (
                        (
                            (
                                [ file_path_cls ]
                            ) if ( 
                                file_path_cls == '/' 
                            ) else (
                                file_path_cls.split( '/' )
                            )
                        ) + (
                            [ file_name ]
                        )
                    ),
                    include_base_path = False
                )
            ),
            #Getting the future base path
            'future_base': (
                GenericGlobalProcedures.joinPath(
                    (
                        (
                            (
                                [ base_path_cls ]
                            ) if ( 
                                base_path_cls == '/' 
                            ) else (
                                base_path_cls.split( '/' )
                            )
                        )
                    ),
                    include_base_path = False
                )
            ),
            #Getting the future base path
            'future_forced': (
                GenericGlobalProcedures.joinPath(
                    (
                        (
                            (
                                []
                            ) if (
                                not ( forced_path_cls ) or
                                forced_path_cls == '/'
                            ) else (
                                (
                                    forced_path_cls.split( '/' )
                                ) if (
                                    '/' in forced_path_cls
                                ) else (
                                    [ forced_path_cls ]
                                )
                            )
                        )
                    ),
                    include_base_path = False
                )
            )
        }
        #Fixing actual path
        if path['actual'][0] != '/':
            path['actual'] = '/' + path['actual']
        #Fixing future base
        if path['future_base'][0] != '/':
            path['future_base'] = '/' + path['future_base']
        #Setting error info if applies
        error_info = None
        #Actual path exists?
        if not os.path.exists( path['actual'] ):
            error_info = 'No existe el archivo en la ruta: [' + path['actual'] + ']. '
            #Future base exists?
            if not os.path.exists( path['future_base'] ):
                error_info = 'No existe la ruta para mover el backup: [' + path['future_base'] + ']. '
        #There are an error info?
        if not ( error_info is None ):
            return {
                'code': 500,
                'path': None,
                'info': error_info,
            }
        #New full file path
        new_full_path = ( path['future_base'] + '/' + path['future_forced'] ).replace( 'C://', 'C:////' ).replace( '//', '/' )
        #Making forced path if doesn exists
        if not os.path.exists( new_full_path ):
            os.makedirs( new_full_path )
        #Revalidate full path
        if not os.path.exists( new_full_path ):
            #No?, location/building error then
            return {
                'code': 500,
                'path': None,
                'info': 'La ruta final no pudo ser encontrada ni creada: [' + new_full_path + ']',
            }
        #Getting the datetime object to set the file name prefix
        dt_obj = (
            (
                GenericGlobalProcedures.getTodayDatetime()
            ) if (
                datetime is None
            ) else (
                datetime
            )
        )
        #Unique file path
        unique_route = (
            (
                getUniqueFilePath(
                    new_full_path + 
                    '/' + 
                    #Datetime prefix
                    (
                        (
                            dt_obj.strftime( '%Y_%m_%d__%H_%M_%S__' )
                        ) if (
                            dt_obj
                        ) else (
                            ''
                        )
                    ) + 
                    '%__CNTR__%___' + 
                    file_name 
                )
            ).replace(
                '//', 
                '/' 
            )
        )
        #Copy?
        play_copy = bkup_style == 2
        #Cheking back up type
        if play_copy:
            shutil.copyfile( path['actual'], unique_route )
        else:
            #Moving file
            os.rename( path['actual'], unique_route )
        #All ok go back
        return {
            'code': 200,
            'path': unique_route,
            'info': 'Backup exitoso. El archivo fue ' + ( '[COPIADO]' if play_copy else '[MOVIDO]' ) + ' satisfactoriamente',
        }

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getClassFromDottedModules( dotted_modules, class_name, __log_obj = None ):
        """
        Returns a class element (non an instance) from a dotted.modules.path
        Args:
            dotted_modules ([string]): A "dotted.path.to.modules"
            class_name ([string]): Class name in [dotted_modules]
            __log_obj ([mixed]): An object to collect the error log from the dotted if exists
        Returns:
            [class]: A class element (non an instance)
        """
        try:
            attr = (
                getattr(
                    importlib.import_module( dotted_modules ), 
                    class_name 
                )
            )
        except Exception as e:
            attr = None
            #Error log?
            if __log_obj:
                __log_obj.setLog(
                    'No se pudo importar dinamicamente el modulo [' + dotted_modules + '][' + class_name + '] ' +
                    'en [GlobalProcedures.getClassFromDottedModules]. Se produjo el error: [' + str( e ) + ']'
                )
        #Attribute go back
        return attr

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def mergeDicts( one, two ):
        """
        Merge two dictionaries
        Args:
            one ([dict]): First dict to merge
            two ([dict]): Second dict to merge
        Returns:
            [dict]: Merged dictionary
        """
        #Python 3.9.0 +
        try:
            return one | two
        except:
            pass
        #Python 3.5 +
        try:
            return { **one, **two }
        except:
            pass
        #Python 2, (or 3.4 or lower)
        copy = one.copy()
        #Updating
        copy.update( two )
        #Copy go back
        return copy

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def replaceFromLastOcurrence( string, locate, replace, how_many = -1 ):
        """
        Replace from last "locate" ocurrence in "string"
        * Splits are done starting at the end and working to the front
        Args:
            string ([string]): String to play
            locate ([string]): String that will be "replace"
            replace ([string]): String that "replace" the "locate"
            how_many ([int]): Max ocurrences to find. Defaults to -1 (all ocurrences)
        Returns:
            [string]: Replaced string
        """
        return (
            str( 
                replace 
            ).join( 
                str( 
                    string 
                ).rsplit( 
                    str( locate ), 
                    int( how_many ) 
                ) 
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def setObjectToJsonString( object ):
        """
        Returns a json string from the object sent
        Args:
            object ([mixed]): Iterable that will be represented in a json string
        Returns:
            [string]: The json string or the error/exception found
        """
        try:
            return json.dumps( object )
        except Exception as e:
            return str( e )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getRandomTrueFalse():
        """
        Returns a random True or False
        Returns:
            [bool]: Random True or Talse
        """
        return randrange( 2 ) == 1
    
    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getRandomBetween( init = 0, end = 1 ):
        """
        Returns a random number between "init" and "end"
        Returns:
            [int]: Random integer
        """
        return random.randint( init, end )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getActualMiliseconds():
        """
        Formats the time to miliseconds
        Returns:
            [int]: Actual miliseconds
        """
        return round( time.time() * 1000 )
    
    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getActualTinyTime( multiplied_by = 1 ):
        """
        Formats the tiny-time to some multiple
        Args:
            multiplied_by ([int]): Amount to expand the tiny-time
        Returns:
            [int]: Actual scoped tiny-time
        """
        return ( time.time() * multiplied_by )
    
    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getTodayDatetime( minus_days = None, plus_days = None ):
        """
        Returns the today datetime
        Args:
            minus_days ([int]): Numbers of days to substract from today
            plus_days ([int]): Numbers of days to add from today
        Returns:
            [Datetime]: Actual date
        """
        today = Datetime.today()
        #Days substractions?
        if minus_days:
            today = today - Timedelta( days = minus_days )
        #Days additions?
        if plus_days:
            today = today + Timedelta( days = plus_days )
        #Today str go back
        return today

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getTodayString( mask = '%Y-%m-%d %H:%M:%S', minus_days = None, plus_days = None ):
        """
        Returns the today string
        Args:
            mask ([string]): String date format, like/similar to: %Y-%m-%d %H:%M:%S
            minus_days ([int]): Numbers of days to substract from today
            plus_days ([int]): Numbers of days to add from today
        Returns:
            [string]: Actual date on the sent mask format
        """
        #Today str go back
        return GenericGlobalProcedures.getTodayDatetime( minus_days = minus_days, plus_days = plus_days ).strftime( mask )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getDateWithMidnightTime( date ):
        """
        Returns a date with midnight
        Returns:
            [datetime]: With date at midnight time
        """
        return Datetime( date.year, date.month, date.day, 0, 0, 0 )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getDateAndTimeFromString( datetime_string, origin_format_mask, return_only = None ):
        """
        Gets a date string and parse it to a datetime or date object, taking the [origin_format_mask] value to perform the parsing
        Args:
            datetime_string ([string]): Date string to parse. Examples: '18/09/19 01:55:19', '12/07/1983, '1983/10/15', etc.
            origin_format_mask ([string]): String with the source date is formatted. Example: '%d/%m/%y %H:%M:%S'
            return_only ([string]): Only the [date] or [time] object is returned. Object [datetime] is back otherwise
        Returns:
            [datetime|date]: Datetime | Date, object
        """
        #Datetime object
        datetime_obj = Datetime.strptime( datetime_string, origin_format_mask )
        #Only date go back?
        if return_only == 'date':
            return datetime_obj.date()
        elif return_only == 'time':
            return datetime_obj.time()
        #No?, datetime go back then
        return datetime_obj

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getFileDateTime( file_path, for_type, path_style = 'relative' ):
        """
        Returns the date-time object
        Args:
            file_path ([mixed]): A [list] with a path pieces or an [string] with the full file-path
            for_type ([string]): Can be only [creation] or [modification] values
            path_style ([bool]): Can be only [relative], [add_app_base] or [since_root]
        Returns:
            [datetime]: Date-time object with the file date-time selected
        """
        #A valid type for?
        if for_type == 'creation':
            create = True
        elif for_type == 'modification':
            create = False
        else:
            return None
        #Getting file path
        if isinstance( file_path, ( list, ) ):
            path = (
                (
                    (
                        GenericGlobalProcedures.getBaseFolderDriveByOs()
                    ) if (
                        path_style == 'since_root'
                    ) else (
                        '' 
                    )
                ) +
                GenericGlobalProcedures.joinPath( file_path, include_base_path = ( path_style == 'add_app_base' ) )
            )
        else:
            path = str( file_path )
        #File date-time go back
        return (
            Datetime.strptime(
                time.ctime(
                    (
                        (
                            os.path.getctime( path )
                        ) if (
                            create
                        ) else (
                            os.path.getmtime( path )
                        )
                    )
                ), 
                '%a %b %d %H:%M:%S %Y'
            )
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getSuperValidatedDate(
        value,
        response_format = '%Y-%m-%d %H:%M:%S', #A [response_format = None] will return the value date/time object
        origin_formats = [
            '%d/%m/%y %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
        ],
        day_first = True
    ):
        """
        Returns the datetime value sent as a [valid date object of string], if applies. Or [None] if something is wrong
        Args:
            value ([string]): Value to format in response
            response_format ([string]): Standard format to set in the response. To return Datetime object, set value as 'obj'
            origin_formats ([list]): List of string masks to validate as [value] date/time format
        Returns:
            [mixed]: Validated date as [Date] object or [string]. None otherwise
        """
        #Object is datetime?
        if isinstance( value, ( Datetime, Date ) ):
            #A valid response format?
            if response_format:
                try:
                    return value.strftime( response_format )
                except:
                    return None
            #Returns the object sent
            return value
        #Fixing the value to play
        some_value = str( value ).strip()
        #Walking all possible date formats that was established on [origin_formats], (first match, first go back)
        for origin_format in origin_formats:
            try:
                #Getting the datetime from an string with format
                datetime_value = GenericGlobalProcedures.getDateAndTimeFromString( some_value, origin_format )
                #A valid response format?, or return the datetime object?
                return (
                    datetime_value.strftime( response_format ) if response_format else datetime_value
                )
            except:
                pass
        #Value still undefined?, final parser try:
        for seq in range( 2 ):
            try:
                #Trying last datetime generic parser
                parsed = (
                    DatetimeParser( 
                        some_value, 
                        dayfirst = ( 
                            seq == ( 0 if day_first else 1 ) 
                        ) 
                    ) 
                )
                #Parsed value format go back
                return (
                    parsed.strftime( response_format ) if response_format else parsed
                )
            except:
                pass
        #Well, no match, sorry
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getSuperValidatedFloat( value, remove_chars = [ '$' ], fix_money_decimals = True, parse_to_float = False ):
        """
        Validate a value as float number format or None
        Args:
            value ([string]): Value to format in response
        Returns:
            [mixed]: Validated string value or None
        """
        #Valid non empty value char?
        if value == '':
            return None
        #Getting string to play
        some_value = str( value ).strip()
        #Removing chars
        for remove_char in remove_chars:
            some_value = some_value.replace( remove_char, '' )
        #Checking for two decimals only
        def checkForTwoDecimals( val, make_fix ):
            #Fixing extra decimals?
            return (
                (
                    val[:2]
                ) if (
                    make_fix and len( val ) > 2
                ) else (
                    val
                )
            )
        #If a comma in the value
        if ',' in some_value:
            parts = some_value.rsplit( ',', 1 )
            #Comma goodbye
            some_value = (
                (
                    parts[0].replace( ',', '' ).replace( '.', '' )
                ) + (
                    '.' if ( len( parts[1] ) < 3 ) else ''
                ) + (
                    parts[1]
                )
            )
        #Removing extra points
        if '.' in some_value:
            parts = some_value.rsplit( '.', 1 )
            #Digit fix
            some_value = (
                (
                    parts[0].replace( '.', '' )
                ) + 
                ( '.' ) +
                (
                    checkForTwoDecimals( parts[1], fix_money_decimals )
                )
            )
            #Decimals found
            decimal_size = len( some_value.rsplit( '.', 1 )[1] )
        else:
            #No decimals then
            decimal_size = 0
        #Valid money decimals?     1456177.9300
        if fix_money_decimals:
            if decimal_size == 1:
                some_value += '0'
            elif decimal_size == 0:
                some_value += '.00'
        #Returning some value
        try:
            if parse_to_float:
                return float( some_value )
            else:
                float( some_value )
                return some_value
        except:
            pass
        #Invalid go back, sorry
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def removeAllInitialStringChars( string_value, remove_char ):
        """
        Removes all initial character like [remove_char] of the string [string_value]
        Args:
            string_value ([string]): Value to perform
            remove_char ([string]): Character to remove from initial string chars
        Returns:
            [string]: Value formatted
        """
        value = copy( string_value )
        #Walking the initial position of the string
        while (
            ( value ) and
            ( value[0] == remove_char )
        ):
            value = value[1:]
        #Formatted string value go back
        return value

    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getIntFromString( int_string, default = None ):
        """
        Returns an integer from a string. If string doesnt match, returns de [default] value sent
        Args:
            int_string ([string]): String to parse into an integer
            default ([mixed]): The default value if string is not an integer
        Returns:
            [mixed]: Integer or [dafault] value
        """
        try:
            return int( str( int_string ) )
        except:
            pass
        #Default return
        return default
    
    #-----------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def getStringUTFBytesLen( value, utf = '16' ):
        """
        Returns the value byte length
        Args:
            value ([string]): The value to mesure
        Returns:
            [int]: Bytes length
        """        
        return len( str( value ).encode( 'utf-' + utf ) )
