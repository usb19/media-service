import json
import time
import re
from utils.decorators import with_request_id
from utils.jwt_utils import extract_jwt_claims
from services.s3_service import generate_upload_url
from services.dynamo_service import insert_media
from utils.response import success, failure
from utils.errors import MediaServiceError, BadRequestError
from utils.logger import logger

# Allowed MIME types
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp"
}
# Max file size: 100 MB
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """
    Replace unsafe characters in filename with underscores.
    Allow only letters, numbers, dot, dash, underscore.
    """
    if not filename:
        return "untitled"

    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    # Avoid names like "." or ".."
    if safe_name.strip("._-") == "":
        return "untitled"
    return safe_name[:255]  # limit length for S3 compatibility


@with_request_id
def lambda_handler(event, context):
    request_id = event["requestId"]
    try:
        logger.info({"requestId": request_id, "event": "START_UPLOAD_HANDLER", "details": event})

        # Extract claims
        claims = extract_jwt_claims(event)
        logger.info({"requestId": request_id, "step": "JWT_EXTRACTED", "claims": claims})

        user_id = claims.get("user_id")
        if not user_id:
            return failure("Invalid token: missing user_id", 400, "BadRequestError")

        # Parse body
        body = json.loads(event.get("body", "{}"))
        content_type = body.get("contentType")
        file_size = body.get("fileSize")  # expected from client (bytes)
        original_filename = body.get("fileName", "")
        caption = body.get("caption", "")
        tags = body.get("tags", [])
        location = body.get("location", None)
        visibility = body.get("visibility", "PUBLIC")

        sanitized_filename = sanitize_filename(original_filename)
        timestamp = int(time.time())

        # === VALIDATIONS ===
        if not content_type:
            return failure("Missing required field: contentType", 400, "BadRequestError")

        if content_type not in ALLOWED_CONTENT_TYPES:
            return failure(f"Unsupported content type: {content_type}", 400, "BadRequestError")

        if file_size is None:
            return failure("Missing required field: fileSize", 400, "BadRequestError")

        if not isinstance(file_size, int) or file_size <= 0:
            return failure("Invalid fileSize: must be a positive integer (bytes)", 400, "BadRequestError")

        if file_size > MAX_FILE_SIZE_BYTES:
            return failure("File size exceeds the maximum limit of 100 MB", 400, "BadRequestError")

        # Generate presigned URL
        media_id, key, url = generate_upload_url(user_id, content_type, request_id)

        # Insert metadata into DynamoDB
        insert_media(
            user_id=user_id,
            media_id=media_id,
            s3_key=key,
            request_id=request_id,
            status="PENDING",
            caption=caption,
            tags=tags,
            location=location,
            visibility=visibility,
            content_type=content_type,
            file_size=file_size,
            file_name=sanitized_filename,
            created_at=timestamp,
            modified_at=timestamp,
            created_by=user_id,
            modified_by=user_id
        )

        response_payload = {
            "uploadUrl": url,
            "mediaId": media_id,
            "requestId": request_id,
            "userId": user_id,
            "fileName": sanitized_filename,
            "caption": caption,
            "tags": tags,
            "location": location,
            "visibility": visibility
        }

        return success(response_payload)

    except MediaServiceError as e:
        return failure(e.message, e.code, error_type=e.__class__.__name__)

    except Exception as e:
        logger.error({
            "requestId": request_id,
            "step": "UPLOAD_HANDLER_EXCEPTION",
            "error": str(e)
        }, exc_info=True)
        return failure("Failed to generate upload URL", 500, "InternalServiceError")
