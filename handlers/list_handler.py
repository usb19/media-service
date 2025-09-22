from utils.decorators import with_request_id
from utils.jwt_utils import extract_jwt_claims
from services.dynamo_service import list_media
from utils.response import success, failure
from utils.errors import MediaServiceError, BadRequestError


ALLOWED_FILTERS = {"status", "mediaId", "createdAfter", "createdBefore"}


@with_request_id
def lambda_handler(event, context):
    request_id = event["requestId"]

    try:
        # 🔑 Extract user from JWT
        claims = extract_jwt_claims(event)
        user_id = claims.get("user_id")
        if not user_id:
            raise BadRequestError("Invalid token: missing user_id")

        # Collect filters from query params
        raw_filters = (event.get("queryStringParameters") or {})
        filters = {}

        for key, value in raw_filters.items():
            if key not in ALLOWED_FILTERS:
                raise BadRequestError(f"Unsupported filter: {key}")

            if key in {"createdAfter", "createdBefore"}:
                try:
                    filters[key] = int(value)
                except ValueError:
                    raise BadRequestError(f"{key} must be an integer timestamp")
            else:
                filters[key] = value

        # Query DynamoDB
        items = list_media(user_id, filters)

        return success({
            "items": items,
            "requestId": request_id
        })

    except MediaServiceError as e:
        return failure(e.message, e.code, error_type=e.__class__.__name__)
    except Exception as e:
        return failure("Failed to list media", 500, "InternalServiceError")
