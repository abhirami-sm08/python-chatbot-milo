from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY","muthoot_fincorp_chatbot_2026")
ALGORITHM = "HS256"

security_bearer = HTTPBearer()

def create_access_token(customer_id: int):

    payload = {
        "sub": str(customer_id),
        "exp": datetime.utcnow() + timedelta(hours=8)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer)
):

    try:

        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return int(payload["sub"])

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session."
        )