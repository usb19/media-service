import json
import pytest
from unittest.mock import patch, MagicMock
from handlers import status_update_handler


def make_event(bucket="media-bucket", key="123/media123"):
    """Helper to generate an S3 event"""
    return {
        "Records": [
            {
                "eventSource": "aws:s3",
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {"name": bucket},
                    "object": {"key": key},
                },
            }
        ]
    }


def test_status_update_success():
    event = make_event()
    with patch("handlers.status_update_handler.mark_media_completed") as mock_mark:
        result = status_update_handler.lambda_handler(event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["message"] == "Media status updated"
        mock_mark.assert_called_once_with("123", "media123")


def test_status_update_no_records():
    event = {"Records": []}
    result = status_update_handler.lambda_handler(event, None)
    body = json.loads(result["body"])

    assert result["statusCode"] == 200
    assert body["message"] == "No records to process"


def test_status_update_invalid_key_format():
    event = make_event(key="invalidkey")
    result = status_update_handler.lambda_handler(event, None)
    body = json.loads(result["body"])

    assert result["statusCode"] == 400
    assert body["error"].startswith("Invalid S3 key format")


def test_status_update_unexpected_error():
    event = make_event()
    with patch("handlers.status_update_handler.mark_media_completed", side_effect=Exception("DB down")):
        result = status_update_handler.lambda_handler(event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 500
        assert body["error"] == "Failed to update media status"
