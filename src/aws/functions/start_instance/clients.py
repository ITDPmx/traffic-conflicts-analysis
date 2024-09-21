import boto3
from constants import region

ssm_client = boto3.client('ssm', region_name=region)
ec2 = boto3.client('ec2', region_name=region)