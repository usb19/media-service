import json
import pytest
from unittest.mock import patch
from handlers import view_handler

@pytest.fixture
def api_event(dummy_jwt):
    return {
        "headers": {"Authorization": dummy_jwt},
        "pathParameters": {"mediaId": "media123"}
    }

def test_view_success(api_event):
    with patch("handlers.view_handler.generate_download_url") as mock_s3:
        mock_s3.return_value = "http://download-url"

        result = view_handler.lambda_handler(api_event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert "downloadUrl" in body

def test_view_missing_media(dummy_jwt):
    event = {"headers": {"Authorization": dummy_jwt}, "pathParameters": {}}
    result = view_handler.lambda_handler(event, None)
    assert result["statusCode"] == 400
