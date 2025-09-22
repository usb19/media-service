import time
from boto3.dynamodb.conditions import Key
from utils.aws_clients import table
from utils.logger import logger
from utils.errors import MediaServiceError


def insert_media(
    user_id: str,
    media_id: str,
    s3_key: str,
    request_id: str,
    status: str = "PENDING",
    caption: str = "",
    tags: list = None,
    location: str = None,
    visibility: str = "PUBLIC",
    content_type: str = None,
    file_size: int = None,
    file_name: str = None,
    created_at: int = None,
    modified_at: int = None,
    created_by: str = None,
    modified_by: str = None,
):
    """
    Insert or update a media record in DynamoDB.
    Includes extended metadata to support Instagram-like features.
    """
    try:
        now = int(time.time())
        item = {
            "PK": f"user#{user_id}",
            "SK": f"media#{media_id}",
            "s3Key": s3_key,
            "requestId": request_id,
            "status": status,
            "caption": caption or "",
            "visibility": visibility,
            "createdAt": created_at or now,
            "modifiedAt": modified_at or now,
            "createdBy": created_by or user_id,
            "modifiedBy": modified_by or user_id,
        }

        if tags:
            item["tags"] = tags

        if location:
            item["location"] = location

        if content_type:
            item["contentType"] = content_type

        if file_size is not None:
            item["fileSize"] = file_size

        if file_name:
            item["fileName"] = file_name

        logger.info({"action": "INSERT_MEDIA", "item": item})
        table.put_item(Item=item)

    except Exception as e:
        logger.error(
            {"action": "INSERT_MEDIA_FAILED", "error": str(e), "mediaId": media_id}
        )
        raise MediaServiceError("Failed to insert media metadata", 500)


def list_media(user_id, filters=None):
    """
    List all media items for a user.
    Supports filtering by status, mediaId, createdAt range.
    """
    filters = filters or {}

    # If createdAt filters exist → use GSI
    if "createdAfter" in filters or "createdBefore" in filters:
        expr = Key("PK").eq(f"user#{user_id}")
        if "createdAfter" in filters and "createdBefore" in filters:
            expr &= Key("createdAt").between(filters["createdAfter"], filters["createdBefore"])
        elif "createdAfter" in filters:
            expr &= Key("createdAt").gte(filters["createdAfter"])
        elif "createdBefore" in filters:
            expr &= Key("createdAt").lte(filters["createdBefore"])

        response = table.meta.client.query(
            TableName=table.name,
            IndexName="GSI_CreatedAt",
            KeyConditionExpression=expr,
        )
        items = response.get("Items", [])
    else:
        # Default query by PK
        response = table.query(
            KeyConditionExpression=Key("PK").eq(f"user#{user_id}")
        )
        items = response.get("Items", [])

    formatted_items = []
    for item in items:
        media_id = item["SK"].replace("media#", "")
        formatted = {
            "mediaId": media_id,
            "s3Key": item.get("s3Key"),
            "status": item.get("status"),
            "requestId": item.get("requestId"),
            "createdAt": int(item.get("createdAt", 0)),
            "modifiedAt": int(item.get("modifiedAt", 0)),
        }
        if "fileName" in item:
            formatted["fileName"] = item["fileName"]
        if "contentType" in item:
            formatted["contentType"] = item["contentType"]
        if "fileSize" in item:
            formatted["fileSize"] = int(item["fileSize"])
        if "caption" in item:
            formatted["caption"] = item["caption"]
        if "tags" in item:
            formatted["tags"] = item["tags"]
        if "location" in item:
            formatted["location"] = item["location"]
        if "visibility" in item:
            formatted["visibility"] = item["visibility"]

        formatted_items.append(formatted)

    # Extra filtering (status, mediaId)
    if "status" in filters:
        formatted_items = [i for i in formatted_items if i["status"] == filters["status"]]
    if "mediaId" in filters:
        formatted_items = [i for i in formatted_items if i["mediaId"] == filters["mediaId"]]

    return formatted_items


def get_media(user_id: str, media_id: str):
    """
    Fetch a single media item for a given user & mediaId.
    Returns the item dict if found, else None.
    """
    response = table.get_item(
        Key={
            "PK": f"user#{user_id}",
            "SK": f"media#{media_id}"
        }
    )
    return response.get("Item")


def cache_presigned_url(user_id: str, media_id: str, url: str, ttl_seconds: int = 300):
    """Store presigned URL in DynamoDB with expiry"""
    expiry = int(time.time()) + ttl_seconds
    table.update_item(
        Key={"PK": f"user#{user_id}", "SK": f"media#{media_id}"},
        UpdateExpression="SET cachedUrl = :url, urlExpiry = :expiry",
        ExpressionAttributeValues={
            ":url": url,
            ":expiry": expiry
        }
    )


def get_cached_presigned_url(item: dict):
    """Return cached presigned URL if still valid"""
    url = item.get("cachedUrl")
    expiry = item.get("urlExpiry")
    now = int(time.time())
    if url and expiry and expiry > now:
        return url
    return None


def delete_media(user_id, media_id):
    """Delete media record for userId + mediaId"""
    table.delete_item(Key={
        "PK": f"user#{user_id}",
        "SK": f"media#{media_id}"
    })


def mark_media_completed(user_id: str, media_id: str):
    """Mark a media item as COMPLETED after upload"""
    table.update_item(
        Key={"PK": f"user#{user_id}", "SK": f"media#{media_id}"},
        UpdateExpression="SET #s = :status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":status": "COMPLETED"},
    )
