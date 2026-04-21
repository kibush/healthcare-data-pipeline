import json
import urllib.parse
import boto3
from datetime import datetime

s3 = boto3.client('s3')

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('PatientRecords')

#simpler parser(conver text ->dictionary )

def parse_patient_data(content):
    data = {}

    for line in content.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    return data



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

    parsed_data = parse_patient_data(content)
    print("Parsed data:", parsed_data)

    # ✅ Ensure required key exists
    if 'PatientID' not in parsed_data:
        print("Missing PatientID — skipping record")
        return

    #DynamoDB saver 
    parsed_data['ProcessedAt'] = datetime.utcnow().isoformat()
    table.put_item(Item=parsed_data)
    print("Data saved to DynamoDB")