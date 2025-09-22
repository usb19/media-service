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
    with patch("handlers.view_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.view_handler.get_media", return_value={"mediaId": "media123"}), \
         patch("handlers.view_handler.get_cached_presigned_url", return_value=None), \
         patch("handlers.view_handler.generate_download_url", return_value="http://download-url"), \
         patch("handlers.view_handler.cache_presigned_url") as mock_cache:

        result = view_handler.lambda_handler(api_event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["downloadUrl"] == "http://download-url"
        mock_cache.assert_called_once()


def test_view_with_cached_url(api_event):
    with patch("handlers.view_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.view_handler.get_media", return_value={"mediaId": "media123", "cachedUrl": "http://cached"}), \
         patch("handlers.view_handler.get_cached_presigned_url", return_value="http://cached"):

        result = view_handler.lambda_handler(api_event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["downloadUrl"] == "http://cached"


def test_view_missing_media_id(dummy_jwt):
    event = {"headers": {"Authorization": dummy_jwt}, "pathParameters": {}}
    result = view_handler.lambda_handler(event, None)
    assert result["statusCode"] == 400
    assert "Missing mediaId" in result["body"]


def test_view_media_not_found(api_event):
    with patch("handlers.view_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.view_handler.get_media", return_value=None):
        result = view_handler.lambda_handler(api_event, None)
        assert result["statusCode"] == 404
        assert "not found" in result["body"]


def test_view_unauthorized_token():
    event = {"headers": {"Authorization": "bad"}, "pathParameters": {"mediaId": "media123"}}
    result = view_handler.lambda_handler(event, None)
    assert result["statusCode"] == 401


def test_view_internal_error(api_event):
    with patch("handlers.view_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.view_handler.get_media", side_effect=Exception("DynamoDB down")):
        result = view_handler.lambda_handler(api_event, None)
        assert result["statusCode"] == 500
        assert "InternalServiceError" in result["body"]
