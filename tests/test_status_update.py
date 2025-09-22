import json
import pytest
from unittest.mock import patch
from handlers import status_update_handler


def test_status_update_no_records():
    event = {"Records": []}
    result = status_update_handler.lambda_handler(event, None)
    body = json.loads(result["body"])

    assert result["statusCode"] == 200
    assert body["message"] == "No records to process"


def test_status_update_success():
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "media-bucket"},
                    "object": {"key": "user123/media123"}
                }
            }
        ]
    }

    with patch("handlers.status_update_handler.mark_media_completed") as mock_mark:
        result = status_update_handler.lambda_handler(event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["message"] == "Media status updated"
        mock_mark.assert_called_once_with("user123", "media123")


def test_status_update_invalid_key_format():
    event = {
        "Records": [
            {"s3": {"bucket": {"name": "media-bucket"}, "object": {"key": "badkey"}}}
        ]
    }

    result = status_update_handler.lambda_handler(event, None)
    body = json.loads(result["body"])

    assert result["statusCode"] == 400
    assert "Invalid S3 key format" in body["error"]


def test_status_update_unexpected_error():
    event = {
        "Records": [
            {"s3": {"bucket": {"name": "media-bucket"}, "object": {"key": "user123/media123"}}}
        ]
    }

    with patch("handlers.status_update_handler.mark_media_completed", side_effect=Exception("DynamoDB down")):
        result = status_update_handler.lambda_handler(event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 500
        assert "InternalServiceError" in body["type"]
