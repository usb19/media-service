import jwt
import datetime

# Function to generate API token - used for testing
def generate_jwt():
    secret = "my-secret"
    algo = "HS256"

    payload = {
        "user_id": "123",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }

    token = jwt.encode(payload, secret, algorithm=algo)
    return token

if __name__ == "__main__":
    print(generate_jwt())
