from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import LoginRequest, LoginResponse
from backend.database import get_db_connection
from backend.auth import create_access_token

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
    """
    SELECT
        C_ID,
        NAME,
        PSWD
    FROM CUSTOMERS
    WHERE UNID = :1
    """,
    (payload.unid,)
)

        row = cursor.fetchone()

        if not row:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Customer ID or Password."
            )

        customer_id, full_name, stored_password = row

        if payload.password.strip().upper() != stored_password.strip().upper():

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Customer ID or Password."
            )

        token = create_access_token(customer_id)

        return {
            "access_token": token,
            "token_type": "bearer",
            "full_name": full_name
        }

    finally:

        cursor.close()
        conn.close()