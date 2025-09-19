import json
import pytest
from unittest.mock import patch
from handlers import delete_handler

@pytest.fixture
def api_event(dummy_jwt):
    return {
        "headers": {"Authorization": dummy_jwt},
        "pathParameters": {"mediaId": "media123"}
    }

def test_delete_success(api_event):
    with patch("handlers.delete_handler.delete_object") as mock_s3, \
         patch("handlers.delete_handler.delete_media") as mock_db:

        mock_s3.return_value = "user123/media123"
        result = delete_handler.lambda_handler(api_event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert "Deleted" in body["message"]

def test_delete_missing_media(dummy_jwt):
    event = {"headers": {"Authorization": dummy_jwt}, "pathParameters": {}}
    result = delete_handler.lambda_handler(event, None)
    assert result["statusCode"] == 400
