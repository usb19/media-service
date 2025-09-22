from utils.decorators import with_request_id
from utils.jwt_utils import extract_jwt_claims
from services.s3_service import generate_download_url
from services.dynamo_service import get_media, cache_presigned_url, get_cached_presigned_url
from utils.response import success, failure
from utils.logger import logger

@with_request_id
def lambda_handler(event, context):
    request_id = event["requestId"]

    try:
        # Extract user
        claims = extract_jwt_claims(event)
        user_id = claims.get("user_id")

        # Validate input
        params = event.get("pathParameters") or {}
        media_id = params.get("mediaId") or (event.get("queryStringParameters") or {}).get("mediaId")
        if not media_id:
            return failure("Missing required parameter: mediaId", 400, "BadRequest")

        # Fetch from Dynamo
        item = get_media(user_id, media_id)
        if not item:
            return failure(f"Media not found for id={media_id}", 404, "NotFound")

        if item.get("status") != "COMPLETED":
            return failure("Media not ready for viewing", 403, "Forbidden")

        # 🔥 Try cached presigned URL first
        cached = get_cached_presigned_url(item)
        if cached:
            logger.info({"requestId": request_id, "step": "CACHE_HIT", "mediaId": media_id})
            return success({"downloadUrl": cached, "requestId": request_id})

        # Otherwise generate new presigned URL
        url = generate_download_url(user_id, media_id)
        cache_presigned_url(user_id, media_id, url, ttl_seconds=300)

        return success({"downloadUrl": url, "requestId": request_id})

    except Exception as e:
        logger.error({"requestId": request_id, "error": str(e)}, exc_info=True)
        return failure("Failed to generate download URL", 500, "InternalServiceError")
