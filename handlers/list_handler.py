from utils.decorators import with_request_id
from utils.jwt_utils import extract_jwt_claims
from services.dynamo_service import list_media
from utils.response import success, failure
from utils.errors import MediaServiceError

@with_request_id
def lambda_handler(event, context):
    request_id = event["requestId"]

    try:
        # 🔑 Extract user from JWT
        claims = extract_jwt_claims(event)
        user_id = claims.get("sub")

        # Query DynamoDB
        items = list_media(user_id)

        return success({
            "items": items,
            "requestId": request_id
        })

    except MediaServiceError as e:
        return failure(e.message, e.code, error_type=e.__class__.__name__)
    except Exception:
        return failure("Failed to list media", 500, "InternalServiceError")
