import boto3
import config

s3 = boto3.client("s3", endpoint_url=config.ENDPOINT, region_name=config.REGION)
dynamodb = boto3.client("dynamodb", endpoint_url=config.ENDPOINT, region_name=config.REGION)

def setup():
    # Create S3 bucket
    try:
        s3.create_bucket(Bucket=config.MEDIA_BUCKET)
        print(f"✅ Created bucket: {config.MEDIA_BUCKET}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"ℹ️ Bucket {config.MEDIA_BUCKET} already exists")

    # Create DynamoDB table
    try:
        dynamodb.create_table(
            TableName=config.MEDIA_TABLE,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"✅ Created table: {config.MEDIA_TABLE}")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"ℹ️ Table {config.MEDIA_TABLE} already exists")

if __name__ == "__main__":
    setup()
