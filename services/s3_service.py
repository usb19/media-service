import uuid
import config
from utils.aws_clients import s3
from utils.common import make_public_url

def generate_upload_url(user_id, content_type="image/jpeg", request_id=None):
    media_id = str(uuid.uuid4())
    key = f"{user_id}/{media_id}"

    extra_metadata = {}
    if request_id:
        extra_metadata["x-amz-meta-request-id"] = request_id

    url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": config.MEDIA_BUCKET,
            "Key": key,
            "ContentType": content_type,
            "Metadata": extra_metadata
        },
        ExpiresIn=300
    )
    
    # 👇 Replace container hostname with localhost for client use
    url = url.replace("localstack", "localhost")
    return media_id, key, make_public_url(url)

def generate_download_url(user_id, media_id):
    key = f"{user_id}/{media_id}"
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": config.MEDIA_BUCKET, "Key": key},
        ExpiresIn=300
    )
    return make_public_url(url)

def delete_object(user_id, media_id):
    key = f"{user_id}/{media_id}"
    s3.delete_object(Bucket=config.MEDIA_BUCKET, Key=key)
    return key