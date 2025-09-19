import json
import pytest
from unittest.mock import patch
from handlers import upload_handler

@pytest.fixture
def api_event(dummy_jwt):
    return {
        "headers": {"Authorization": dummy_jwt},
        "body": json.dumps({"contentType": "image/jpeg"})
    }

def test_upload_success(api_event):
    with patch("handlers.upload_handler.generate_upload_url") as mock_s3, \
         patch("handlers.upload_handler.insert_media") as mock_db:

        mock_s3.return_value = ("media123", "user123/media123", "http://upload-url")
        result = upload_handler.lambda_handler(api_event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert "uploadUrl" in body
        assert "mediaId" in body

def test_upload_missing_token():
    event = {"headers": {}, "body": "{}"}
    result = upload_handler.lambda_handler(event, None)
    assert result
