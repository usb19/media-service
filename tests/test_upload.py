import json
import pytest
from unittest.mock import patch
from handlers import upload_handler


def make_event(body=None, token="Bearer test.jwt.token"):
    return {
        "headers": {"Authorization": token},
        "body": json.dumps(body or {"contentType": "image/jpeg", "fileSize": 1024, "fileName": "pic.jpg"})
    }


def test_upload_success():
    with patch("handlers.upload_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.upload_handler.generate_upload_url", return_value=("media123", "user123/media123", "http://upload-url")), \
         patch("handlers.upload_handler.insert_media"):

        result = upload_handler.lambda_handler(make_event(), None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["mediaId"] == "media123"
        assert "uploadUrl" in body
        assert body["userId"] == "user123"


def test_upload_missing_token():
    event = {"headers": {}, "body": "{}"}
    result = upload_handler.lambda_handler(event, None)
    assert result["statusCode"] == 401
    assert "Invalid token" in result["body"]


@pytest.mark.parametrize("body,error", [
    ({}, "Missing required field: contentType"),
    ({"contentType": "video/mp4", "fileSize": 100}, "Unsupported content type"),
    ({"contentType": "image/jpeg"}, "Missing required field: fileSize"),
    ({"contentType": "image/jpeg", "fileSize": -1}, "Invalid fileSize"),
    ({"contentType": "image/jpeg", "fileSize": 200*1024*1024}, "File size exceeds"),
])
def test_upload_validation_errors(body, error):
    with patch("handlers.upload_handler.extract_jwt_claims", return_value={"user_id": "user123"}):
        result = upload_handler.lambda_handler(make_event(body=body), None)
        assert result["statusCode"] == 400
        assert error in result["body"]


def test_upload_missing_user_id():
    with patch("handlers.upload_handler.extract_jwt_claims", return_value={}):
        result = upload_handler.lambda_handler(make_event(), None)
        assert result["statusCode"] == 400
        assert "missing user_id" in result["body"]


def test_upload_exception():
    with patch("handlers.upload_handler.extract_jwt_claims", side_effect=Exception("boom")):
        result = upload_handler.lambda_handler(make_event(), None)
        assert result["statusCode"] == 500
        assert "InternalServiceError" in result["body"]
