from utils.decorators import with_request_id
from utils.jwt_utils import extract_jwt_claims
from services.s3_service import delete_object
from services.dynamo_service import delete_media
from utils.response import success, failure
from utils.errors import MediaServiceError, BadRequestError

@with_request_id
def lambda_handler(event, context):
    request_id = event["requestId"]

    try:
        # 🔑 Extract user from JWT
        claims = extract_jwt_claims(event)
        user_id = claims.get("sub")

        # Path param check
        path = event.get("pathParameters") or {}
        media_id = path.get("mediaId")
        if not media_id:
            raise BadRequestError("Missing required path parameter: mediaId")

        # Delete from S3 + DynamoDB
        key = delete_object(user_id, media_id)
        delete_media(user_id, media_id)

        return success({
            "message": f"Deleted {key}",
            "requestId": request_id
        })

    except MediaServiceError as e:
        return failure(e.message, e.code, error_type=e.__class__.__name__)
    except Exception:
        return failure("Failed to delete media", 500, "InternalServiceError")
