import json
from utils.decorators import with_request_id
from utils.jwt_utils import extract_jwt_claims
from services.s3_service import generate_upload_url
from services.dynamo_service import insert_media
from utils.response import success, failure
from utils.errors import MediaServiceError, BadRequestError
from utils.logger import logger


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
            raise BadRequestError("Invalid token: missing user subject")

        # Parse body
        body = json.loads(event.get("body", "{}"))
        content_type = body.get("contentType", "image/jpeg")
        logger.info({"requestId": request_id, "step": "BODY_PARSED", "contentType": content_type})

        # Generate presigned URL
        media_id, key, url = generate_upload_url(user_id, content_type, request_id)
        logger.info({
            "requestId": request_id,
            "step": "UPLOAD_URL_GENERATED",
            "mediaId": media_id,
            "s3Key": key,
            "uploadUrl": url
        })

        # Insert metadata into DynamoDB
        insert_media(user_id, media_id, key, request_id)
        logger.info({
            "requestId": request_id,
            "step": "METADATA_INSERTED",
            "mediaId": media_id,
            "userId": user_id,
            "s3Key": key
        })

        response_payload = {
            "uploadUrl": url,
            "mediaId": media_id,
            "requestId": request_id,
            "userId": user_id
        }
        logger.info({"requestId": request_id, "step": "UPLOAD_HANDLER_SUCCESS", "response": response_payload})

        return success(response_payload)

    except MediaServiceError as e:
        logger.error({"requestId": request_id, "step": "UPLOAD_HANDLER_FAILED", "error": e.message, "type": e.__class__.__name__})
        return failure(e.message, e.code, error_type=e.__class__.__name__)
    except Exception as e:
        logger.error({"requestId": request_id, "step": "UPLOAD_HANDLER_EXCEPTION", "error": str(e)}, exc_info=True)
        return failure("Failed to generate upload URL", 500, "InternalServiceError")
