import json
from services.dynamo_service import get_media, mark_media_completed
from utils.response import success, failure
from utils.errors import MediaServiceError
from utils.logger import logger


def lambda_handler(event, context):
    logger.info("StatusUpdate Lambda invoked")
    try:
        logger.debug(f"Raw event: {json.dumps(event)}")

        records = event.get("Records", [])
        if not records:
            logger.warning("No S3 records found in event")
            return success({"message": "No records to process"})

        for record in records:
            key = record["s3"]["object"]["key"]
            bucket = record["s3"]["bucket"]["name"]

            logger.info(f"Processing S3 event: bucket={bucket}, key={key}")

            # Expect key format: userId/mediaId
            parts = key.split("/", 1)
            if len(parts) != 2:
                logger.error(f"Invalid S3 key format: {key}")
                return failure(f"Invalid S3 key format: {key}", 400, "BadRequest")

            user_id, media_id = parts
            logger.debug(f"Extracted user_id={user_id}, media_id={media_id}")

            # 🔎 Fetch the record first
            item = get_media(user_id, media_id)
            if not item:
                logger.warning(f"No matching record found for key={key}")
                continue

            if item.get("status") == "COMPLETED":
                logger.info(f"Media {media_id} already marked COMPLETED, skipping update")
                continue

            # ✅ Update only if not already completed
            mark_media_completed(user_id, media_id)
            logger.info(f"Marked mediaId={media_id} as COMPLETED for userId={user_id}")

        logger.info("All records processed successfully")
        return success({"message": "Media status updated"})

    except MediaServiceError as e:
        logger.warning(f"Business error: {e.message}")
        return failure(e.message, e.code, error_type=e.__class__.__name__)

    except Exception as e:
        logger.exception("Unexpected error while processing S3 event")
        return failure("Failed to update media status", 500, "InternalServiceError")
