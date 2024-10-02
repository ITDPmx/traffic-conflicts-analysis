import configparser

from Generic.Global.Borg import Borg

#Singleton class to avoid multiple DBMS connection pointers/calls
class GenericConfig(Borg ):
    
    #Global objects pointers
    __globals = None

    #Release configurations
    __system_release_sections = None

    #Configurations obj
    __config = {
        'obj': None,
        'sections': None,
    }

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the configurations are made just once (singleton class)
        Returns:
            [None]: None
        """#Global objects pointers retriving
        self.__globals = globals
        #Setting the fundamental release ini file sections
        self.__system_release_sections = self.__getReleaseSections()
        #Main ini config parser object
        self.__config['obj'] = configparser.ConfigParser()
        #Reading all configurations
        self.__config['obj'].read(
            self.__globals['__global_procedures'].joinPath(
                [
                    'Public',
                    'config',
                    'system.release.' + ( self.__system_release_sections['release']['mode'] ) + '.config.ini',
                ]
            )
        )
        #Setting all sections found
        self.__config['sections'] = self.__config['obj'].sections()
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __getReleaseSections( self, ):
        """
        Gets the system release configurations sections of the main base [system.release.config.ini] file
        Returns:
            [dict]: Dictionary with the [system.release.config.ini] file configurations sections
        """
        #Release ini parser obj
        obj = configparser.ConfigParser()
        #Reading fundamental ini file
        obj.read(
            self.__globals['__global_procedures'].joinPath(
                [
                    'Public',
                    'config',
                    'system.release.config.ini',
                ]
            )
        )
        #Section datas
        datas = {}
        #Walking all fundamental ini sections
        for section in obj.sections():
            datas[section] = dict( obj.items( section ) )
        #Sections datas go back
        return datas

    #-----------------------------------------------------------------------------------------------------------------------------
    def __getByPrefix( self, prefix ):
        """
        Gets the values for the sections with the prefix sent
        Args:
            prefix ([string]): Section prefix to get
        Returns:
            [mixed]: Mixed
        """
        res = {}
        #Walking all config sections
        for section in self.__config['sections']:
            if str( section ).find( prefix ) == 0:
                res[section] = dict( self.__config['obj'].items( section ) )
        #Results go back
        return res

    #-----------------------------------------------------------------------------------------------------------------------------
    def __get( self, section ):
        """
        Gets the value for the section sent
        Args:
            section ([string]): Section/Option to get
        Returns:
            [mixed]: Mixed
        """
        if section in self.__config['sections']:
            return dict( self.__config['obj'].items( section ) )
        #Rising a not found exception
        raise Exception(
            'Error en seccion de configuracion: GenericConfig.__get( "' + section + '" ). No se puede ' +
            'encontrar el [match] en el archivo de configuraciones: ' +
            '[system.release.' + ( self.__system_release_sections['release']['mode'] ) + '.config.ini]'
        )

    #-----------------------------------------------------------------------------------------------------------------------------
    def getByPrefix( self, prefix ):
        """
        Gets the values for the sections with the prefix sent
        Args:
            prefix ([string]): Section prefix to get
        Returns:
            [mixed]: Mixed
        """
        return self.__getByPrefix( prefix )

    #-----------------------------------------------------------------------------------------------------------------------------
    def get( self, section ):
        """
        Gets the value for the option sent
        Args:
            option ([string]): Option to get
        Returns:
            [mixed]: Mixed
        """
        return self.__get( section )
    
    #-----------------------------------------------------------------------------------------------------------------------------
    def getDbPrepareConfigVars( self, ):
        """
        Gets the Db prepare configurations from main base [system.release.config.ini] file [db_prepare] section
        Returns:
            [dict]: Dictionary with all db prepare configuration vars
        """
        return self.__system_release_sections['db_prepare']
