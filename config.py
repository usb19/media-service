import os

# Environment
ENV = os.getenv("ENV", "local")   # local | dev | prod

# AWS / LocalStack
REGION = os.getenv("AWS_REGION", "us-east-1")

LOCALSTACK_HOST = os.getenv("LOCALSTACK_HOSTNAME", "localhost")

ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", f"http://{LOCALSTACK_HOST}:4566") # Used only for localstack deafult to aws for other env
# External (for API responses to clients)
PUBLIC_ENDPOINT = os.getenv("PUBLIC_ENDPOINT", "http://localhost:4566") # This will be your bucket base path https://<bucket>.s3.amazonaws.com

# Resources
MEDIA_BUCKET = os.getenv("MEDIA_BUCKET", "media-bucket")
MEDIA_TABLE = os.getenv("MEDIA_TABLE", "MediaTable")

# Auth
JWT_SECRET = os.getenv("JWT_SECRET", "my-secret")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Lambda config (for deployment)
LAMBDA_ROLE = os.getenv("LAMBDA_ROLE", "arn:aws:iam::000000000000:role/lambda-role")
LAMBDA_RUNTIME = os.getenv("LAMBDA_RUNTIME", "python3.9")
