import uuid
import config
from utils.aws_clients import s3
from utils.common import make_public_url
from utils.errors import MediaServiceError


def generate_upload_url(user_id, content_type="image/jpeg", request_id=None):
    """
    Generate a presigned URL for uploading an object to S3.
    Also replaces 'localstack' with 'localhost' for client-friendly usage.
    """
    media_id = str(uuid.uuid4())
    key = f"{user_id}/{media_id}"

    extra_metadata = {}
    if request_id:
        extra_metadata["x-amz-meta-request-id"] = request_id

    try:
        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": config.MEDIA_BUCKET,
                "Key": key,
                "ContentType": content_type,
                "Metadata": extra_metadata,
            },
            ExpiresIn=300,
        )

        # Replace container hostname with localhost for client use
        url = url.replace("localstack", "localhost")

        return media_id, key, make_public_url(url)

    except Exception as e:
        raise MediaServiceError(f"Failed to generate upload URL: {str(e)}", 500)


def generate_download_url(user_id, media_id):
    """
    Generate a presigned URL for downloading an object from S3.
    """
    key = f"{user_id}/{media_id}"
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": config.MEDIA_BUCKET, "Key": key},
            ExpiresIn=300,
        )

        return make_public_url(url)

    except Exception as e:
        raise MediaServiceError(f"Failed to generate download URL: {str(e)}", 500)


def delete_object(user_id: str, media_id: str):
    """
    Delete an object from S3 bucket.
    """
    key = f"{user_id}/{media_id}"
    try:
        s3.delete_object(Bucket=config.MEDIA_BUCKET, Key=key)
        return key
    except Exception as e:
        raise MediaServiceError(f"Failed to delete from S3: {str(e)}", 500)
