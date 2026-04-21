# Healthcare Data Pipeline (AWS)

## 📌 Overview
This project demonstrates a serverless healthcare data processing pipeline using AWS.

Patient data files uploaded to S3 automatically trigger a Lambda function that:
- Parses patient information
- Validates required fields
- Separates valid and invalid records
- Prevents recursive processing

---

## ⚙️ Architecture
S3 → Lambda → Validation → Output to S3

---

## 🔍 Features
- Automated file processing using AWS Lambda
- Data validation (PatientID, Name, Diagnosis, Age)
- Error handling for missing or invalid data
- Recursive trigger protection to prevent infinite loops

---

## 🧪 Example Use Case
A healthcare system uploads patient intake files:
- Valid records → stored for analytics
- Invalid records → flagged for correction

---

## 🛠️ Tech Stack
- AWS S3
- AWS Lambda
- Python (boto3)

---

## 🚀 Future Improvements
- Store valid records in DynamoDB
- Add API Gateway for external access
- Implement monitoring with CloudWatch
