import json
import pytest
from unittest.mock import patch
from handlers import list_handler


def make_event(token="Bearer test.jwt.token", query=None):
    event = {
        "headers": {"Authorization": token},
    }
    if query:
        event["queryStringParameters"] = query
    return event


def test_list_success():
    with patch("handlers.list_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.list_handler.list_media", return_value=[{"mediaId": "1"}]):
        result = list_handler.lambda_handler(make_event(), None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert "items" in body
        assert body["items"][0]["mediaId"] == "1"


def test_list_with_filters():
    filters = {"status": "COMPLETED", "createdAfter": "1700000000"}
    with patch("handlers.list_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.list_handler.list_media") as mock_list:
        mock_list.return_value = [{"mediaId": "2", "status": "COMPLETED"}]

        result = list_handler.lambda_handler(make_event(query=filters), None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        mock_list.assert_called_once()
        assert body["items"][0]["status"] == "COMPLETED"


def test_list_missing_user_id():
    with patch("handlers.list_handler.extract_jwt_claims", return_value={}):
        result = list_handler.lambda_handler(make_event(), None)
        assert result["statusCode"] == 400
        assert "missing user_id" in result["body"]


def test_list_unauthorized_token():
    result = list_handler.lambda_handler({"headers": {"Authorization": "bad"}}, None)
    assert result["statusCode"] == 401


def test_list_media_service_error():
    with patch("handlers.list_handler.extract_jwt_claims", return_value={"user_id": "user123"}), \
         patch("handlers.list_handler.list_media", side_effect=Exception("DB down")):
        result = list_handler.lambda_handler(make_event(), None)
        assert result["statusCode"] == 500
        assert "InternalServiceError" in result["body"]
