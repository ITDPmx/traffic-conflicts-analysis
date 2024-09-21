import time
import requests
import concurrent.futures
from constants import instance_ids, services, DOCKER_UP_STATUS, CONTAINER_STATUS_COMMAND, PORT_STATUS_COMMAND
from clients import ssm_client, ec2


def execute_command(command, instance_ids):
    response = ssm_client.send_command(
        InstanceIds=instance_ids,
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands': [command]
        },
    )
    
    command_id = response['Command']['CommandId']
    
    time.sleep(1)
    
    output = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_ids[0],
    )
        
    return output['StandardOutputContent']


def get_ip():
    response = ec2.describe_instances(InstanceIds=instance_ids)
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            public_ip = instance.get('PublicIpAddress')
            # private_ip = instance.get('PrivateIpAddress')
            return public_ip
        
        
def services_up():
    for service, port in services.items():
        if not is_service_running(service, instance_ids):
            print(f"{service} is not running")
            return False
        if not is_port_listening(port):
            print(f"Port {port} is not listening")
            return False
    return True
    
    
def is_service_running(container_name, instance_ids):
   container_status = execute_command(CONTAINER_STATUS_COMMAND.format(container_name=container_name), instance_ids)
   print(f"{container_name} status is {container_status}")

   return container_status.strip() == DOCKER_UP_STATUS
 
 
def is_port_listening(port):
    output_status = execute_command(PORT_STATUS_COMMAND.format(port=port), instance_ids)
    output_status = output_status.strip()
    print(f"port {port} status is {output_status}")
    return bool(output_status)


def send_post_request(url, data):
    try:
        requests.post(url, json=data)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def unawaited_request(url, data):
    # Send POST request without waiting for the result
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(send_post_request, url, data)
        
