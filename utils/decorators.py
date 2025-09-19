# utils/decorators.py
import functools
import logging
import uuid
from utils.response import success, failure

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def with_request_id(func):
    """Decorator to ensure every request has a requestId and consistent logging."""

    @functools.wraps(func)
    def wrapper(event, context, *args, **kwargs):
        # Generate or reuse requestId
        request_id = (
            event.get("requestId")
            or event.get("requestContext", {}).get("requestId")
            or str(uuid.uuid4())
        )
        event["requestId"] = request_id  # ensure availability

        # ENTRY log
        logger.info({
            "event": "ENTER",
            "handler": func.__name__,
            "requestId": request_id,
            "path": event.get("path"),
            "method": event.get("httpMethod"),
            "hasHeaders": bool(event.get("headers")),
            "hasBody": bool(event.get("body")),
            "pathParameters": event.get("pathParameters"),
            "queryParameters": event.get("queryStringParameters"),
        })

        try:
            response = func(event, context, *args, **kwargs)

            # If response dict exists, inject requestId for consistency
            if isinstance(response, dict) and "body" in response:
                import json
                try:
                    body = json.loads(response["body"])
                    body["requestId"] = request_id
                    response["body"] = json.dumps(body)
                except Exception:
                    pass  # don’t break on body mutation

            # EXIT log
            logger.info({
                "event": "EXIT",
                "handler": func.__name__,
                "requestId": request_id,
                "status": "success",
                "statusCode": response.get("statusCode") if isinstance(response, dict) else None,
            })
            return response

        except Exception as e:
            logger.error({
                "event": "EXIT",
                "handler": func.__name__,
                "requestId": request_id,
                "status": "error",
                "errorType": type(e).__name__,
                "errorMessage": str(e),
            }, exc_info=True)

            # Ensure failure response always includes requestId
            return failure(
                message="Internal server error",
                code=500,
                error_type=type(e).__name__,
                request_id=request_id
            )

    return wrapper
