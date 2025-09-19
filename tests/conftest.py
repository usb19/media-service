import pytest
import jwt
import config

@pytest.fixture
def dummy_jwt():
    payload = {"sub": "user123"}
    token = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")
    return f"Bearer {token}"
