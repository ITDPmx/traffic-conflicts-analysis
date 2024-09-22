import os
from email_utils import send_email_with_oauth2
import requests
import urllib

import boto3
region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)

DATA_ENDPOINT = "https://tca.mexico.itdp.org/api/email_data"
REDIRECT_ENDPOINT = "https://tca.mexico.itdp.org/dashboard/historial"

instance_ids = ["i-02a33facac910baba"]

def send_email(destination: str, subject: str, link: str, user_name: str, video_name: str, date_str: str):
    return {"Result": send_email_with_oauth2(destination, subject, link, user_name, video_name, date_str)}


def get_email_data(video_id: str):
    data = requests.get(f"{DATA_ENDPOINT}/{video_id}").json()["data"]["emailInfo"]
    return {
        "destination": data["user"]["email"],
        "subject": "Tu video ha sido procesado!",
        "link": REDIRECT_ENDPOINT,
        "user_name": data["user"]["name"],
        "date_str": data["createdAt"],
        "video_name": data["name"]
    }

def lambda_handler(event, context):
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    video_id = os.path.splitext(key.split("/")[-1])[0]
    
    # Remove summary prefix
    video_id = video_id[7:]
    
    print(f"Processing video with id: {video_id}")
    
    email_data = get_email_data(video_id)
    
    print("email_data: ", email_data)
    send_email(
        destination=email_data["destination"],
        subject=email_data["subject"],
        link=email_data["link"],
        user_name=email_data["user_name"],
        video_name=email_data["video_name"],
        date_str=email_data["date_str"]
    )
    
    # Turn off instance
    ec2.stop_instances(InstanceIds=instance_ids)
    
    return {
        'statusCode': 200,
        'body': 'Email sent successfully'
    }

if __name__ == '__main__':
    DATA_ENDPOINT = "http://localhost:3000/api/email_data"
    lambda_handler({"Records": [{"s3": {"bucket": {"name": "test"}, "object": {"key": "cm1chk50n00005t02plax1hr2.csv"}}}]}, None)