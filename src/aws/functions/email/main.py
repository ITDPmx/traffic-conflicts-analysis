import os
from pydantic import BaseModel
from email_utils import send_email_with_oauth2
import requests
import urllib

class Email(BaseModel):
    destination: str
    subject: str
    link: str
    user_name: str
    video_name: str
    date_str: str
    

DATA_ENDPOINT = "https://tca.mexico.itdp.org/api/email_data"
REDIRECT_ENDPOINT = "https://tca.mexico.itdp.org/dashboard/historial"

def send_email(emailData: Email):
    return {"Result": send_email_with_oauth2(emailData.destination, emailData.subject, emailData.link, emailData.user_name, emailData.video_name, emailData.date_str)}


def get_email_data(video_id: str):
    data = requests.get(f"{DATA_ENDPOINT}/{video_id}").json()["data"]["emailInfo"]
    return Email(destination=data["user"]["email"], subject="Tu video ha sido procesado!", 
                 link=REDIRECT_ENDPOINT, user_name=data["user"]["name"],\
                 date_str=data["createdAt"], video_name=data["name"])

def lambda_handler(event, context):
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    video_id = os.path.splitext(key.split("/")[-1])[0]
    
    return {
        'statusCode': 200,
        'body': send_email(get_email_data(video_id))
    }

if __name__ == '__main__':
    DATA_ENDPOINT = "http://localhost:3000/api/email_data"
    lambda_handler({"Records": [{"s3": {"bucket": {"name": "test"}, "object": {"key": "cm1chk50n00005t02plax1hr2.csv"}}}]}, None)