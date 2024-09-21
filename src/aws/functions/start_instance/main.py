import json
import time
import requests
import urllib

from utils import execute_command, get_ip, services_up, unawaited_request
from constants import instance_ids, DOCKER_COMPOSE_COMMAND
from clients import ec2

def lambda_handler(event, context):
    # Start the instance
    ec2.start_instances(InstanceIds=instance_ids)
    
    print("Instance started")
    
    # Retrieve data of uploaded video
       
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    # Await unitl ec2 acquires public ip
    while ec2_ip := get_ip() is None:
        time.sleep(1)
        
    print("EC2 IP obtained")

    
    # Run docker compose command
    execute_command(DOCKER_COMPOSE_COMMAND, instance_ids)
    
    print("Executed docker compose command")

    
    # Wait until services are up
    while not services_up():
        time.sleep(1)
        
    print("Services in EC2 are running")

    
    url = f"http://{ec2_ip}:8000/birdsEyeView"
    body = {
        "bucket": bucket,
        "path": key,
        "id": key.split("/")[-1]
    }
    
    unawaited_request(url, body)
    
    print("Sent request to EC2 API")

    return {
        'statusCode': 200,
        'body': "Called BEV service with url: " + url + " and body: " + json.dumps(body)
    }
