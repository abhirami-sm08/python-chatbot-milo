from fastapi import APIRouter, HTTPException, status
from models.schemas import LoginRequest, LoginResponse
from database import get_db_connection
from auth import verify_password, create_access_token

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT CUSTOMER_ID, FULL_NAME, PASSWORD_HASH FROM CUSTOMERS WHERE EMAIL = :1", 
            (payload.email,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        
        customer_id, full_name, password_hash = row
        
        # Security Note: If your mock data password isn't encrypted yet, direct matching string comparison can be used temporarily
        if payload.password != password_hash and not verify_password(payload.password, password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
            
        token = create_access_token(customer_id)
        return {"access_token": token, "token_type": "bearer", "full_name": full_name}
        
    finally:
        cursor.close()
        conn.close()