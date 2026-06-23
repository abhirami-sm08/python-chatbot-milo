from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.config import settings

ALGORITHM = settings.ALGORITHM

security_bearer = HTTPBearer()


def create_access_token(customer_id: int):
    payload = {
        "sub": str(customer_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return int(payload["sub"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session."
        )

def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
):
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return int(payload["sub"])
    except JWTError:
        return None