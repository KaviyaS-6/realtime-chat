from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")
print("JWT SECRET:", SECRET_KEY)
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