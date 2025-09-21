
# 📄 Media Service
Scalable image upload and metadata service built on AWS (S3, DynamoDB, API Gateway, Lambda). Supports presigned URL uploads, metadata persistence, image listing with filters, secure viewing/download, and deletion. Includes LocalStack setup for local development, unit tests, and API documentation on Python.

## 📦 Prerequisites

Make sure you have the following installed:

- Python 3.9+  
- [pip](https://pip.pypa.io/en/stable/)  
- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/)  
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)  
- [awscli-local (`awslocal`)](https://github.com/localstack/awscli-local) *(optional but handy)*  

---

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/usb19/media-service
cd media-service
```

---

## 2. Setup Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate    # On Windows
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start LocalStack with Docker Compose

```bash
docker-compose up -d
```

---

## 5. Deploy to LocalStack

Use the provided `Makefile` commands.

```bash
make deploy-local
```

This will build and deploy the Lambda functions, API Gateway, DynamoDB table, and S3 bucket inside LocalStack.

---

## 6. Attach S3 Event to Trigger Status Update (Local stack runs into dead loop when both added together)

After deployment, attach the S3 event to call the **StatusUpdate Lambda** whenever a file is uploaded.
Two ways to do it

### 1. List all generated functions
```bash

AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws \
  --endpoint-url=http://localhost:4566 --region us-east-1 \
  lambda list-functions \
  --query 'Functions[*].FunctionName' \
  --output text | tr '\t' '\n'

```
and copy the `media-service-UploadFunction-<id>` and replace it below

```bash
    AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
    aws --endpoint-url=http://localhost:4566 --region us-east-1 \
    s3api put-bucket-notification-configuration \
    --bucket media-bucket \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [
        {
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:media-service-MediaStatusUpdateFunctio-<id>",
            "Events": ["s3:ObjectCreated:*"]
        }
        ]
    }'

```

or 

 ### 2. using awslocal
```bash
    awslocal s3api put-bucket-notification-configuration   --bucket media-bucket   --notification-configuration '{
    "LambdaFunctionConfigurations": [
      {
        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:MediaStatusUpdateFunction",
        "Events": ["s3:ObjectCreated:*"]
      }
    ]
  }'
```

---

## 7. Run Locally

```bash
make start-api
```

---

## 8. API Postman Collection
[API Collection](https://implatform.postman.co/workspace/My-Workspace~734a0e1a-52ed-4b72-8505-c20b4625588a/collection/15992747-164e1fcc-8c91-4777-89df-c8c26d0b214a?action=share&creator=15992747&active-environment=15992747-e77d8032-d266-4199-be9c-367338566df7)

---

## 9. Generate API token with 
```bash
python generate_token.py
```

---

## 10. Run Tests

```bash
make test
```

---

## 11. Tear Down

To remove the deployed stack and clean up:

```bash
make delete-local
docker-compose down
```

---



