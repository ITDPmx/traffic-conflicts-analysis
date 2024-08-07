import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

html_template = """
<html>
  <body>
    <h1 style="color:blue;">¡Tus resultados están listos!</h1>
    <p>Accede a tus <a href="{link}">resultados</a>.</p>
  </body>
</html>
"""


def send_email_with_oauth2(to_email, subject, link):
    creds = None
    # token.json saves credentials after the first login
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in, this generates a token.json file
    # Otherwise refresh token using contents fron token.json
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        # When running on AWS Lambda, the file system is read-only
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except Exception as error:
            pass

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(html_template.format(link=link), 'html')
    message['to'] = to_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    message = {
        'raw': raw
    }

    try:
        message = service.users().messages().send(userId='me', body=message).execute()
        return f'Email sent successfully: {message["id"]}'
    except Exception as error:
        return "An error occurred: %s" % error



if __name__ == '__main__':
    # Example usage
    to_email = 'X@gmail.com'
    subject = 'Tus resultados están listos!'
    link = 'Lorem ipsum'
    send_email_with_oauth2(to_email, subject, link)

