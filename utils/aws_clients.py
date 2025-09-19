import boto3
import config

print(f"[AWS CLIENTS] Using LocalStack endpoint: {config.ENDPOINT}")

s3 = boto3.client("s3", region_name=config.REGION, endpoint_url=config.ENDPOINT)
dynamodb = boto3.resource("dynamodb", region_name=config.REGION, endpoint_url=config.ENDPOINT)
table = dynamodb.Table(config.MEDIA_TABLE)
