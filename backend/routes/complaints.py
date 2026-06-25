from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.database import get_db_connection
from backend.auth import get_current_user

router = APIRouter()

class ComplaintRequest(BaseModel):
    message_context: str
    issue_type: str
    issue_notes: Optional[str] = ""

class ComplaintResponse(BaseModel):
    complaint_id: int
    message_context: str
    issue_type: str
    issue_notes: str
    status: str
    created_at: datetime

@router.post("/complaints")
def submit_complaint(payload: ComplaintRequest, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Note: Depending on Oracle version, returning INTO may be needed, but we can just return success.
        cursor.execute(
            """
            INSERT INTO COMPLAINTS (C_ID, MESSAGE_CONTEXT, ISSUE_TYPE, ISSUE_NOTES, STATUS)
            VALUES (:1, :2, :3, :4, 'OPEN')
            """,
            (current_user, payload.message_context, payload.issue_type, payload.issue_notes)
        )
        conn.commit()
        return {"status": "success", "message": "Complaint submitted successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.get("/complaints", response_model=List[ComplaintResponse])
def get_complaints(current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            SELECT COMPLAINT_ID, MESSAGE_CONTEXT, ISSUE_TYPE, ISSUE_NOTES, STATUS, CREATED_AT
            FROM COMPLAINTS
            WHERE C_ID = :1
            ORDER BY CREATED_AT DESC
            """,
            (current_user,)
        )
        rows = cursor.fetchall()
        
        complaints = []
        for row in rows:
            complaint_id, msg_context, issue_type, issue_notes, stat, created_at = row
            complaints.append({
                "complaint_id": complaint_id,
                "message_context": msg_context.read() if hasattr(msg_context, 'read') else str(msg_context),
                "issue_type": issue_type,
                "issue_notes": issue_notes.read() if hasattr(issue_notes, 'read') else str(issue_notes),
                "status": stat,
                "created_at": created_at
            })
            
        return complaints
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()
