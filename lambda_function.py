import json
import urllib.parse
import boto3
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Event:", json.dumps(event))

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    # 🚫 Recursive protection
    if key.startswith("processed/"):
        print(f"Skipping already processed file: {key}")
        return

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')

    print("File content:", content)