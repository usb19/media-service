import json
import pytest
from unittest.mock import patch
from handlers import list_handler

@pytest.fixture
def api_event(dummy_jwt):
    return {"headers": {"Authorization": dummy_jwt}}

def test_list_success(api_event):
    with patch("handlers.list_handler.list_media") as mock_list:
        mock_list.return_value = [{"SK": "media#1"}]

        result = list_handler.lambda_handler(api_event, None)
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert "items" in body
        assert len(body["items"]) == 1

def test_list_unauthorized():
    event = {"headers": {"Authorization": "badtoken"}}
    result = list_handler.lambda_handler(event, None)
    assert result["statusCode"] == 401
