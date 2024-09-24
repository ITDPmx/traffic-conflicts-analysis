import os
import json
import time
import requests
import urllib

from utils import execute_command, get_ip, services_up, unawaited_request
from constants import instance_ids, DOCKER_COMPOSE_COMMAND, DEFAULT_MATRIX_URL, BEV_URL, BEV_URL_DEFAULT
from clients import ec2

def lambda_handler(event, context):
    # Start the instance
    start_time = time.time()
    ec2.start_instances(InstanceIds=instance_ids)
    
    print("Instance started")
    
    # Retrieve data of uploaded video
       
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    video_id = os.path.splitext(key.split("/")[-1])[0] 
    
    # Await unitl ec2 acquires public ip
    ec2_ip = get_ip()
    while ec2_ip is None or ec2_ip == "" or ec2_ip == False or ec2_ip == "None" or ec2_ip.lower() == "false":
        ec2_ip = get_ip()
        time.sleep(1)
        
    print("EC2 IP obtained: " + ec2_ip)
    
    # Delay before running docker compose command
    time.sleep(10)
    
    # Run docker compose command
    res = execute_command(DOCKER_COMPOSE_COMMAND, instance_ids)
    
    print(f"Executed docker compose command({res})")
    
    # Wait until services are up
    while not services_up():
        time.sleep(1)
        
    print("Services in EC2 are running")

    time.sleep(10)
    
    # Check if the API has default matrix
    response = requests.get(DEFAULT_MATRIX_URL + "?id=" + video_id)
    
    print("Response from default matrix API: ", response.json())
    
    use_default_matrix = response.json()["data"]["usesDefaultMatrix"]
    
    if use_default_matrix:
        url = BEV_URL_DEFAULT.format(ec2_ip=ec2_ip)
    else:
        url = BEV_URL.format(ec2_ip=ec2_ip)
        
    print("URL used: " + url)
    
    body = {
        "bucket": bucket,
        "path": key,
        "id": video_id
    }
    
    print("Before request to EC2 API")
    print("time: ", time.time() - start_time)
    unawaited_request(url, body)
    
    print("Sent request to EC2 API")

    return {
        'statusCode': 200,
        'body': "Called BEV service with url: " + url + " and body: " + json.dumps(body)
    }
