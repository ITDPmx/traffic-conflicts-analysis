import smtplib
import os
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import zipfile

from zipfile import ZipFile


#Singleton class to avoid multiple DBMS connection pointers/calls
class GenericMailer( ):
    
    #Globals cursors
    __globals = None

    #Paths to save the mailer CSVs
    __mailer_file_path = None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __init__( self, globals ):
        """
        Class builder, all the configurations are made just once (singleton class)
        Returns:
            [None]: None
        """
        #Globals cursors pointers
        self.__globals = globals
        #Mailer file paths
        self.__mailer_file_path = {
            '_lobby': self.__globals['__global_procedures'].joinPath( [ 'Public', 'mailer_file' ] ),
            '_store': self.__globals['__global_procedures'].joinPath( [ 'Public', 'mailer_file', 'sent' ] ),
        }
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __logMessage( self, style, type, mailer_name, message_for ):
        """
        Executes a query for the connection sent
        Args:
            mailer_name ([string]): Mailer to log for
            message_for ([string]): SQL string code to be executed
        Returns:
            [None]: None
        """
        #Notice
        if style == 'notice':
            if type == 'send_mail_step':
                self.__globals['__log'].setLog(
                    'Mailer [' + mailer_name + '] dice: ' + str( message_for )
                )
        #Error
        if style == 'error': 
            if type == 'mailer_disabled':
                self.__globals['__log'].setLog(
                    ( 'Mailer [' + mailer_name + '] dice: ' + str( message_for ) ),
                    type = 'warning',
                    code = 500
                )
            #Invalid connection driver
            elif type == 'send_mail':
                self.__globals['__log'].setLog(
                    (
                        'Ha fallado el envio de correo por parte del "mailer" [' + mailer_name + ']: ' + 
                        str( message_for )
                    ),
                    type = 'error',
                    code = 500
                )
        #Nothing go back
        return None  

    #-----------------------------------------------------------------------------------------------------------------------------
    def __sendMail( self, email, attachments = None, mailer = 'default', sleep = 5 ):
        """
        Send an email with the info configs
        Args:
            email ([dict]): Dictionary with the sender configurations
                            Example:
                            email = {
                                #Configuration sender name, for set the server account
                                'server': 'default',
                                #Subject text
                                'subject': 'Some subject',
                                #Message text/html
                                'content': (
                                    '<p>Some message</p>'
                                ),
                            }
            attachments ([list]): With all string paths of the files to attach
                                  Example:
                                  attachments = [
                                    {
                                        #List of a file path
                                        'list_file_path': [ 'DirA', 'DirB', ..., 'FileName.ext' ],
                                        #Move the file to the sent folder
                                        'move_to_sent': True|False,
                                        #Rename the sent file with .done extension
                                        'rename_sent': True|False,
                                    },
                                    ...,
                                  ],
            mailer ([string]): That indicates the INI file config options to set the mailer
            sleep ([int]): Amount of seconds to sleep the execution per each mailer try. To avoid massive cicled senders/spam
        Returns:
            [None]: None
        """           
        mailer_name = 'mailer_' + mailer   
        #Mail directors
        mailer = self.__globals['__config'].get( mailer_name )
        mail_conn = self.__globals['__config'].get( mailer['server'] )
        #Mailer is not abled?
        if mailer['abled'] == '0':
            #Disabled notification
            self.__logMessage( 'error', 'mailer_disabled', mailer_name, 'El envio de correo esta deshabilitado.' )
            #Nothing go back!
            return None
        #Email from 
        email_from = mailer['from']
        email_to = mailer['to'] #email_to = 'mariaelena.garcia@telefonica.com'
        #Server config
        server_host = mail_conn['host']
        server_port = mail_conn['port'] if ( 'port' in mail_conn ) else None
        server_user = mail_conn['user'] if ( 'user' in mail_conn ) else None
        server_pass = mail_conn['pass'] if ( 'pass' in mail_conn ) else None
        #TLS flag
        server_tls = ( str( mail_conn['tls'] ) == '1' )  if ( 'tls' in mail_conn ) else None
        #Mail main object
        mail = MIMEMultipart()
        #Email people
        mail['From'] = email_from
        mail['To'] = email_to
        #Mail subject assignation
        mail['Subject'] = email['subject']        
        #Setting the main content
        mail.attach(
            MIMEText(
                (
                    """
                    <html>
                        <head></head>
                        <body>
                            """ + email['content'] + """
                        </body>
                    </html>
                    """
                ), 
                'html' 
            ) 
        )
        #Notice on body attachment
        self.__logMessage( 'notice', 'send_mail_step', mailer_name, 'Se ha adjuntado el contenido del correo' )
        #Appending attachments
        if not ( attachments is None ):
            #Walking valid attachments
            for attachment in attachments:
                #Getting the attach MIME
                item = MIMEBase( 'application', "octet-stream" )
                item_path = self.__globals['__global_procedures'].joinPath( attachment['list_file_path'] )
                #Setting the attachet-file payload read-cursor
                item.set_payload(
                    open( item_path, "rb" ).read()
                )
                #Setting mail header
                item.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename = attachment['list_file_path'][-1]
                )
                #Base64 encode
                encoders.encode_base64( item )  
                #Final literal attach to mail
                mail.attach( item )
                #Notice on file attachment
                self.__logMessage( 'notice', 'send_mail_step', mailer_name, 'Se ha adjuntado el archivo: [' + item_path + ']' )
        #Trying the sending procedure
        try:
            #Setting smtp server
            server = (
                ( 
                    smtplib.SMTP( server_host ) 
                ) 
                if server_port is None else
                (
                    smtplib.SMTP( server_host, server_port )
                )
            )
            #Notice on server SMTP
            self.__logMessage( 
                'notice', 
                'send_mail_step', 
                mailer_name, 
                'Objeto [smtplib.SMTP] con host:port [' + str( server_host ) + ':' + str( server_port ) + '] creado' 
            )
            #Only if an account is setted
            if not ( server_user is None ) and not ( server_pass is None ):
                server.ehlo()
                #TLS security?
                if server_tls:
                    server.starttls()
                #Server login
                server.login( server_user, server_pass )
                #Notice on server SMTP
                self.__logMessage(
                    'notice', 
                    'send_mail_step', 
                    mailer_name, 
                    'Objeto server [smtplib.SMTP] loggeado con "user": [' + server_user + '] y "pass": [********]' 
                )
            #Sender flag
            sent = None
            #Notice log message step 1
            self.__logMessage(
                'notice', 
                'send_mail_step', 
                mailer_name, 
                (
                    '----------------------------------\n' +
                    'Inicia intento de envio de correo\n' +
                    '*********************************' 
                )            
            )        
            #Sender go!
            server.sendmail(
                email_from, 
                email_to.split( ',' ),
                mail.as_string()
            )
            #Server goodbye
            server.quit()
            #Notice log message step 2
            self.__logMessage( 
                'notice', 
                'send_mail_step', 
                mailer_name,
                ( 
                    '----------------------------------\n' +
                    'Se ha completado el envio del correo electronico por parte del sistema\n' +
                    'Verifique el correo en las respectivas cuentas destinatarias\n' +
                    'En caso de no recibir el mail, podria verificar:\n' +
                    '-La configuracion del servidor de correo\n' +
                    '-La configuracion de la cuenta de correo destinataria\n' +
                    '-Puertos abiertos al servidor de correo conectado\n'+
                    '*********************************' 
                )
            )
            #Sent is ok
            sent = True
        #Exception error log?
        except Exception as e:
            self.__logMessage( 'error', 'send_mail', mailer_name, str( e ) )
            #Sent is wrong
            sent = False
        #Everything is done, valid and ok?
        if sent and not ( attachments is None ):
            #Notice log message step 1
            self.__logMessage(
                'notice', 
                'send_mail_step', 
                mailer_name, 
                (
                    '----------------------------------\n' +
                    'Verificando la estrategia para los\n'+
                    'archivos adjuntos enviados\n' +
                    '*********************************' 
                )
            )
            #Moving attachments then
            for attachment in attachments:
                #Delete the attachment?
                if ( 'remove_from_disc' in attachment ) and attachment['remove_from_disc']:
                    self.__dropFile( mailer_name, attachment['list_file_path'] )
                #If file won't be deleted, play standard management procedure 
                else:
                    #Moving the sent file?
                    if ( 'move_to_sent' in attachment ) and attachment['move_to_sent']:
                        attachment_name = attachment['list_file_path'][-1]
                        #Final list path
                        final_list_path = (
                            [ self.__mailer_file_path['_store'] ] + [ attachment_name ]
                        )
                        self.__globals['__global_procedures'].renameFile(
                            #Origin name
                            attachment['list_file_path'],
                            #Destination name
                            final_list_path,
                        )
                        #Moved file log
                        self.__logMessage(
                            'notice', 
                            'send_mail_step', 
                            mailer_name, 
                            (
                                '-Adjunto [' + attachment_name + '] movido al folder de enviados [../Public/mailer_file/sent]'
                            )
                        )
                    else:
                        final_list_path = attachment['list_file_path']
                    #Rename the sent file?
                    if ( 'rename_sent' in attachment ) and attachment['rename_sent']:
                        new_final_list_path = [] + final_list_path
                        new_final_list_path[-1] = new_final_list_path[-1] + '.done'
                        #Then rename
                        self.__globals['__global_procedures'].renameFile(
                            #Old name
                            final_list_path,
                            #New name
                            new_final_list_path,
                        )
                        #Renamed file log
                        self.__logMessage(
                            'notice', 
                            'send_mail_step', 
                            mailer_name, 
                            (
                                '-Adjunto renombrado como: [' + new_final_list_path[-1] + ']'
                            )
                        )
        #Protection to: do not overload the mail server cicling fast requests!
        time.sleep( sleep )
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __dropFile( self, mailer_name, list_file_path ):
        """
        Drops the file of the list_file_path sent
        Args:
            list_file_path ([list]): Full file path LIST [ ../path/to/folder, file_name ] of the file to be deleted
        Returns:
            [None]: None
        """
        full_file_path = self.__globals['__global_procedures'].joinPath( list_file_path )
        #Delete only valid file paths
        if os.path.exists( full_file_path ):
            os.remove( full_file_path )
            #Removed log
            self.__logMessage(
                'notice', 
                'send_mail_step', 
                mailer_name, 
                (
                    '-Adjunto [' + list_file_path[-1] + '] eliminado/borrado del disco duro'
                )
            )
        #File doesn't exist log
        else:
            self.__logMessage(
                'notice', 
                'send_mail_step', 
                mailer_name, 
                (
                    '-Adjunto [' + list_file_path[-1] + '] no encontrado al intentar eliminarlo'
                )
            )
        #Nothing go back
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def __sendMailWithPandaCsv( self, info, zipped = True ):
        """
        Sets a CSV and send an email with the info configs
        Args:
            info ([dict]): Dictionary with the sender-message configurations!
                           Example:
                           info = {
                                'self': self,                     #Client object that calls this sender
                                'type': 'CONCILIATION_RESULTS',   #Type of service to provide
                                'attachments': [                  #Attachments list
                                    ...,
                                    {
                                        'panda': pandas_object,                #Panda object
                                        'panda_column_renames': {              #Exchange columns names dictionary
                                            'original_colname': 'new_colname', # --> On empty dict: {}, no exchange will be set
                                            ...,
                                        },
                                        'panda_column_actives': {              #Active columns. CSV will be only with this cols!
                                            'field_column': {                  # --> On None, all columns will be deployed on CSV
                                                'label': 'Field label',
                                            },
                                            ...,
                                        }
                                        'csv_base_name': 'CSVFileBaseName',    #Base name of the CSV file
                                        'csv_separator': '|',                  #CSV separator char
                                        'csv_encoding': 'utf-8',               #CSV encoding
                                        'csv_max_rows': 40000,                 #By default: [40000] rows
                                    },
                                    ...,
                                ],
                                'email': {                       #Data to configure the email
                                    'server': 'default',         #Configuration sender name, for set the server account
                                    'subject': 'Some subject',   #Subject text
                                    'content': (                 #Message text/html
                                        '<p>Some message</p>'
                                    ),
                                }
                           }
        Returns:
            [None]: None
        """
        #:::::::::::::::::::::::::::::::::::::::::
        #Separates the pandas by max ammount of rows
        def getSeparatedPandas( panda, max_rows ):
            #Len check
            if( len( panda ) > max_rows ):
                #Splitting pandas by short and long sizes
                panda_short, panda_long = panda[:max_rows], panda[max_rows:]
                #And returning the cutted panda plus another eval!
                return [ panda_short ] + getSeparatedPandas( panda_long, max_rows )
            #Len is ok?, panda go back then!
            return [ panda ]
        #:::::::::::::::::::::::::::::::::::::::::
        #Mail with panda only abled for this object type:
        if (
            info['type'] == 'CONCILIATION_RESULTS'
        ):
            #Procedure vars
            today_str = self.__globals['__global_procedures'].getTodayString( mask = '__%Y_%m_%d__%H_%M_%S.txt' )
            #Zipped logic?
            if zipped:
                default_max_panda_rows = 230000
                default_max_csv_filesize = 45000000
            else:
                default_max_panda_rows = 25000
                default_max_csv_filesize = 9000000
            #Mails collector
            attachments = []
            #Walking attachments
            for attach in info['attachments']:
                #Logging column rename
                self.__logMessage( 
                    'notice', 
                    'send_mail_step', 
                    info['email']['server'], 
                    'Renombrando columnas del panda: ' + attach['csv_base_name'] 
                )
                #Active columns to deploy on CSV
                active_csv_columns = []
                #Walking all panda active columns
                for field_column in attach['panda_column_actives']:
                    if (
                        (
                            'label' in attach['panda_column_actives'][field_column]
                        ) and (
                            attach['panda_column_actives'][field_column]['label']
                        )
                    ):
                        active_csv_columns.append(
                            attach['panda_column_actives'][field_column]['label']
                        )
                    else:
                        active_csv_columns.append( field_column )
                #Renamed panda setting
                renamed_panda = (
                    attach['panda'].rename(
                        columns = attach['panda_column_renames'],
                    )
                )
                #Sepparating pandas
                pandas = (
                    getSeparatedPandas(
                        renamed_panda, 
                        (
                            ( 
                                attach['csv_max_rows']
                            ) if ( 
                                ( 
                                    'csv_max_rows' in attach 
                                ) and
                                (
                                    attach['csv_max_rows']
                                )
                            ) else ( 
                                default_max_panda_rows 
                            ) 
                        )
                    )
                )
                #All parts
                all_parts = str( len( pandas ) )
                #Collecting by parts
                part = 1
                #Walking parts collection
                for panda in pandas:
                    #Only for valid pandas
                    if len( panda ) > 0:
                        #Setting the file CSV name
                        file_name = (
                            attach['csv_base_name'] + 
                            '_Parte_' + str( part ) + '_de_' + all_parts + 
                            today_str 
                        )
                        #Dir list of the full path
                        list_file_path = [ self.__mailer_file_path['_lobby'], file_name ]
                        #Pandas CSV saving
                        panda.to_csv(
                            self.__globals['__global_procedures'].joinPath( list_file_path ),
                            index = False,
                            sep = attach['csv_separator'],
                            encoding = attach['csv_encoding'],
                            columns = (
                                (
                                    active_csv_columns
                                ) if (
                                    len( active_csv_columns ) > 0
                                ) else (
                                    list( panda.columns )
                                )
                            )
                        )
                        #Appending the builded attachment
                        attachments.append(
                            {
                                'list_file_path': list_file_path,
                                'remove_from_disc': zipped,
                                'send_on_mail': ( not zipped ),
                                'move_to_sent': True,
                                'rename_sent': True,
                            }
                        )
                        #Another part
                        part += 1
            #Collects all attachments by mail that will be sent
            attaches_by_mail = [
                #Starts with empty data
                {
                    'attachments': [],
                    'files_size': 0,
                }
            ]
            #Sending emails by attachment
            for i, attachment in enumerate( attachments ):
                file_size = os.path.getsize( self.__globals['__global_procedures'].joinPath( attachment['list_file_path'] ) )
                #Appended to email?
                appended = False
                #The attachment walks all attaches by mail asking for a right [file_size] partner
                for attach_by_mail in attaches_by_mail:
                    if (
                        attach_by_mail['files_size'] < default_max_csv_filesize and
                        ( file_size + attach_by_mail['files_size'] ) < default_max_csv_filesize
                    ):
                        attach_by_mail['attachments'].append( attachment )
                        attach_by_mail['files_size'] += file_size
                        #Appended flag to True
                        appended = True
                        #Adding no more
                        break
                #If the attachment doesn't found partner, attachs new mail
                if not appended:
                    attaches_by_mail.append(
                        {
                            'attachments': [ attachment ],
                            'files_size': file_size,
                        }
                    )
            #Sending emails by organized and sized attachments
            for i, attach_by_mail in enumerate( attaches_by_mail ):
                if len( attach_by_mail['attachments'] ) > 0:
                    #Part
                    part = ' - Correo No. ' + str( i + 1 ) + ' de ' + str( len( attaches_by_mail ) )
                    #Zip logic?
                    if zipped:
                        zip_file_path = (
                            [
                                self.__mailer_file_path['_lobby'],
                                self.__globals['__global_procedures'].getUniqueGenericId( 'ConciliacionMovistarZip_' ) + '.zip'
                            ]
                        )
                        #Building the zip object/file 
                        zip_obj = (
                            ZipFile(
                                self.__globals['__global_procedures'].joinPath( zip_file_path ), 
                                'w', 
                                zipfile.ZIP_DEFLATED
                            )
                        )
                        #Walking all attachments
                        for attached in attach_by_mail['attachments']:
                            #Adding multiple files to the zip
                            zip_obj.write(
                                self.__globals['__global_procedures'].joinPath(
                                    [
                                        attached['list_file_path'][0],
                                        attached['list_file_path'][1]
                                    ]
                                ),
                                #Avoiding full folder structure on zipped file/folder
                                attached['list_file_path'][1]
                            )
                        #Closing the zip object
                        zip_obj.close()
                        #Final mail attachments
                        final_attachments = [
                            {
                                'list_file_path': zip_file_path,
                                'remove_from_disc': ( not zipped ),
                                'send_on_mail': zipped,
                                'move_to_sent': True,
                                'rename_sent': True,
                            }
                        ]
                        #Now, dropping all garbage zip free attachments
                        for attached in attach_by_mail['attachments']:
                            self.__dropFile( 'sin-mailer-en-logica-de-zip', attached['list_file_path'] )
                    else:
                        final_attachments = attach_by_mail['attachments']
                    #Sending email
                    self.__sendMail(
                        #Email data
                        {
                            'server': info['email']['server'],
                            'subject': info['email']['subject'] + part,
                            'content': info['email']['content'] + ( '<p>' + part + '</p>' ),
                        }, 
                        #Attachments
                        final_attachments,
                        #Configuration INI key
                        info['email']['server']
                    )
                    #To avoid repeated file names impacts
                    time.sleep( 1 )
        #Go back nothing
        return None

    #-----------------------------------------------------------------------------------------------------------------------------
    def sendMailWithPandaCsv( self, info ):
        """
        Send an email with the info configs
        Args:
            info ([string]): Dictionary with the sender-message configurations!
        Returns:
            [mixed]: Mixed ?
        """
        return self.__sendMailWithPandaCsv( info )

    #-----------------------------------------------------------------------------------------------------------------------------
    def sendMail( self, info ):
        """
        Send an email with the info configs
        Args:
            info ([string]): Dictionary with the sender-message configurations!
        Returns:
            [mixed]: Mixed ?
        """
        return None
