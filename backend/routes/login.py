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
            WHERE EMAIL = :1
            """,
            (payload.email,)
        )

        row = cursor.fetchone()

        # 1. Check if user exists
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        customer_id, full_name, stored_password = row

        # 2. Verify password (ensure we use payload.password to match your schema update)
        if payload.password != stored_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # 3. Generate token
        token = create_access_token(customer_id)

        # 4. Construct response dictionary
        response_data = {
            "access_token": token,
            "token_type": "bearer",
            "full_name": full_name
        }
        
        return response_data

    except HTTPException as http_ex:
        # Re-raise FastAPI HTTP exceptions cleanly so they don't turn into 500s
        raise http_ex
    except Exception as e:
        # Catch genuine database or system bugs and print them to your terminal
        print(f"Database/Internal Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()