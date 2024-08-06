import boto3
region = 'XXXXX'

ec2 = boto3.client('ec2', region_name=region)
s3 = boto3.client('s3')

instances = ["i-XXXXXXXXXXXXXXXXX"]


def get_ip():
    response = ec2.describe_instances(InstanceIds=instances)
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            public_ip = instance.get('PublicIpAddress')
            private_ip = instance.get('PrivateIpAddress')
            return public_ip, private_ip

def lambda_handler(event, context):
    ec2.start_instances(InstanceIds=instances)
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    response = s3.get_object(Bucket=bucket, Key=key)
    print("CONTENT TYPE: " + response['ContentType'])
    print('started your instances: ' + str(instances))
    print("aws ips:")
    print(get_ip())
    
    