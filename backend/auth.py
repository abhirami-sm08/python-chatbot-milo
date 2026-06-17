from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "muthoot_fincorp_chatbot_2026")
print("SECRET_KEY =", SECRET_KEY)

ALGORITHM = "HS256"

security_bearer = HTTPBearer()

def create_access_token(customer_id: int):

    payload = {
        "sub": str(customer_id),
        "exp": datetime.utcnow() + timedelta(hours=8)
    }

    print("Creating JWT Payload:", payload)

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    print("Generated Token:", token)

    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer)
):

    try:
        print("\n========== JWT DEBUG ==========")
        print("Authorization Scheme:", credentials.scheme)
        print("Received Token:", credentials.credentials)

        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("Decoded Payload:", payload)
        print("Customer ID:", payload["sub"])
        print("===============================\n")

        return int(payload["sub"])

    except JWTError as e:

        print("\n========== JWT ERROR ==========")
        print("Error:", str(e))
        print("===============================\n")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session."
        )