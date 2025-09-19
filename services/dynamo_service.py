from boto3.dynamodb.conditions import Key
from utils.aws_clients import table

def insert_media(user_id, media_id, s3_key, request_id, status="PENDING"):
    table.put_item(Item={
        "PK": f"user#{user_id}",
        "SK": f"media#{media_id}",
        "s3Key": s3_key,
        "status": status,
        "requestId": request_id
    })

def list_media(user_id):
    response = table.query(
        KeyConditionExpression=Key("PK").eq(f"user#{user_id}")
    )
    return response.get("Items", [])

def delete_media(user_id, media_id):
    table.delete_item(Key={
        "PK": f"user#{user_id}",
        "SK": f"media#{media_id}"
    })
