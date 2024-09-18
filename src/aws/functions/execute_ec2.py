import boto3
import urllib.parse
import time

region = 'us-east-1'

ssm_client = boto3.client('ssm', region_name=region)

def execute_command(command, instance_id):
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            'commands': [command]
        },
    )
    
    command_id = response['Command']['CommandId']
    print(command_id)
    print("Response:", response)
    
    time.sleep(1)
    
    output = ssm_client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id,
    )
    
    print("Complete output:", output)
    
    return output['StandardOutputContent']


def lambda_handler(event, context):

    command = 'ls'
    instance_id = "i-"

    result = execute_command(command, instance_id)
    print("result:", result)
    