# Healthcare Data Pipeline (AWS)

This project processes patient data using AWS services.

## Architecture
- S3 uploads trigger Lambda
- Lambda validates patient data
- Valid data → processed/valid/
- Invalid data → processed/invalid/

## Features
- Recursive trigger protection
- Data validation
- Cloud-based automation

## Tech Stack
- AWS S3
- AWS Lambda
- Python (boto3)