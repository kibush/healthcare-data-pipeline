import json
import urllib.parse
import boto3
from datetime import datetime

# Optimizing lambda performance: initialize resources outside handler
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('PatientRecords')

s3 = boto3.client('s3')


# Parse patient text file into dictionary
def parse_patient_data(content):
    data = {}

    for line in content.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    return data


# Validate parsed patient data
def validate_patient_data(parsed_data):
    errors = []

    # Required fields
    required_fields = ["PatientID", "Name", "Diagnosis", "Age"]

    for field in required_fields:
        value = parsed_data.get(field)

        if value is None:
            errors.append(f"Missing field: {field}")
        elif value.strip() == "":
            errors.append(f"Empty field: {field}")

    # Stop deeper checks if required fields are missing/empty
    if errors:
        return errors

    # Validate PatientID
    patient_id = parsed_data.get("PatientID", "").strip()
    if not patient_id.isdigit():
        errors.append("PatientID must be numeric")

    # Validate Name
    name = parsed_data.get("Name", "").strip()
    if not any(char.isalpha() for char in name):
        errors.append("Name must contain letters")

    # Validate Age
    age_value = parsed_data.get("Age", "").strip()
    if not age_value.isdigit():
        errors.append("Age must be a number")
    else:
        age_int = int(age_value)
        parsed_data["Age"] = age_int

        if age_int < 0 or age_int > 120:
            errors.append("Age out of valid range (0-120)")

    return errors


def lambda_handler(event, context):
    try:
        print("Event:", json.dumps(event))

        # Get bucket and file name
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

        print(f"Bucket: {bucket}")
        print(f"File: {key}")

        # Prevent recursive processing
        if key.startswith("processed/"):
            print(f"Skipping already processed file: {key}")
            return {
                'statusCode': 200,
                'body': json.dumps('Skipped processed file')
            }

        # Read uploaded file
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        print("File content:")
        print(content)

        # Parse content
        parsed_data = parse_patient_data(content)
        print("Parsed data:", parsed_data)

        # Validate content
        errors = validate_patient_data(parsed_data)

        if len(errors) == 0:
            result = "VALID"
            print("Valid patient data file")
        else:
            result = "INVALID"
            print("Invalid patient data file")
            print("Errors:", errors)

        # Extract filename only
        filename = key.split("/")[-1].replace(".txt", ".json")

        # Build output path
        if result == "VALID":
            output_key = f"processed/valid/{filename}"
        else:
            output_key = f"processed/invalid/{filename}"

        # Build output JSON
        output_data = {
            "source_file": key,
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "result": result,
            "errors": errors,
            "parsed_data": parsed_data
        }

        # Save record to DynamoDB
        item = {
            'PatientID': str(parsed_data.get('PatientID', 'UNKNOWN')),
            'Name': str(parsed_data.get('Name', '')),
            'Age': parsed_data.get('Age', 0) if isinstance(parsed_data.get('Age'), int) else 0,
            'Diagnosis': str(parsed_data.get('Diagnosis', '')),
            'Status': result,
            'ProcessedAt': datetime.utcnow().isoformat() + "Z",
            'SourceFile': key,
            'Errors': errors
             }

        table.put_item(Item=item)
        print("Saved record to DynamoDB:", item)

        # Save validation result to S3
        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(output_data, indent=2),
            ContentType='application/json'
        )

        print(f"Validation result saved to: {output_key}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Validation complete',
                'result': result,
                'errors': errors,
                'parsed_data': parsed_data,
                'output_file': output_key
            })
        }

    except Exception as e:
        print("Error during Lambda execution:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Processing failed',
                'error': str(e)
            })
        }