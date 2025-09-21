import jwt
import config
from utils.errors import UnauthorizedError

def extract_jwt_claims(event):
    headers = event.get("headers") or {}
    auth_header = headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    try:
        claims = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGO])
        return claims
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise UnauthorizedError(f"Invalid token: {str(e)}")
