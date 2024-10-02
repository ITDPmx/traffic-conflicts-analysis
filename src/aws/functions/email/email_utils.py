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
    <p>Hola {user_name},</p> 
    <p>Los resultados de tu video "{video_name}" subido el {date_str} se terminaron de procesar.</p>
    <p>Da clic <a href="{link}">aquí</a> para acceder a tus resultados.</p>
  </body>
</html>
"""


def send_email_with_oauth2(to_email, subject, link, user_name, video_name, date_str):
    creds = None
    token_path = 'token.json'

    # Check if token.json exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Handle case where creds are invalid or expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                # Handle the refresh error by deleting token.json
                # os.remove(token_path)
                print("Token has been revoked. Please re-authenticate.")
                return "Token revoked. Please re-authenticate."
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the refreshed token
        try:
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error saving refreshed token: {e}")

    # Build Gmail service and send the email
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(html_template.format(link=link, user_name=user_name, video_name=video_name, date_str=date_str), 'html')
    message['to'] = to_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}
    
    try:
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        return f'Email sent successfully: {sent_message["id"]}'
    except Exception as error:
        return f"An error occurred: {error}"


if __name__ == '__main__':
    # Example usage
    to_email = 'X@gmail.com'
    subject = 'Tus resultados están listos!'
    link = 'Lorem ipsum'
    user_name = 'Usuario'
    video_name = 'My video'
    date_str = '2021-09-10'
    send_email_with_oauth2(to_email, subject, link, user_name, video_name, date_str)

