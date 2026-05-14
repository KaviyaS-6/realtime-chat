from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "MYSECRETKEY"

ALGORITHM = "HS256"

def create_token(username):

    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def verify_token(token):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload["sub"]

    except:

        return None