import json

def success(body, code=200):
    return {"statusCode": code, "body": json.dumps(body)}

def failure(message, code=500, error_type="SystemError"):
    return {
        "statusCode": code,
        "body": json.dumps({
            "error": message,
            "type": error_type
        })
    }
