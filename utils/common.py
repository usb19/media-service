import config

def make_public_url(url: str) -> str:
    """
    Replace internal LocalStack endpoint with public-facing one.
    """
    return url.replace(config.ENDPOINT, config.PUBLIC_ENDPOINT)
