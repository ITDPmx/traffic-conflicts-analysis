import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_email_with_oauth2(to_email, subject, body):
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
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    message = {
        'raw': raw
    }

    try:
        message = service.users().messages().send(userId='me', body=message).execute()
        print(f'Email sent successfully: {message["id"]}')
    except Exception as error:
        print(f'An error occurred: {error}')

# Example usage
to_email = 'some?mail@domain.mx'
subject = 'Test Email with OAuth2'
body = 'Lorem ipsum'

send_email_with_oauth2(to_email, subject, body)
