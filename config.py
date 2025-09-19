import os

# Environment
ENV = os.getenv("ENV", "local")   # local | dev | prod

# AWS / LocalStack
REGION = os.getenv("AWS_REGION", "us-east-1")

LOCALSTACK_HOST = os.getenv("LOCALSTACK_HOSTNAME", "localhost")

if ENV == "local":
    ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", f"http://{LOCALSTACK_HOST}:4566")
else:
    # In dev/prod, boto3 should hit real AWS (no endpoint override)
    ENDPOINT = None

# Resources
MEDIA_BUCKET = os.getenv("MEDIA_BUCKET", "MediaBucket")
MEDIA_TABLE = os.getenv("MEDIA_TABLE", "MediaTable")

# Auth
JWT_SECRET = os.getenv("JWT_SECRET", "my-secret")
JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Lambda config (for deployment)
LAMBDA_ROLE = os.getenv("LAMBDA_ROLE", "arn:aws:iam::000000000000:role/lambda-role")
LAMBDA_RUNTIME = os.getenv("LAMBDA_RUNTIME", "python3.9")
