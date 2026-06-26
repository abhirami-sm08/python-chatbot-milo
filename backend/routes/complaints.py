from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from backend.database import get_db_connection
from backend.auth import get_current_user

router = APIRouter()

class ComplaintRequest(BaseModel):
    message_context: str
    issue_type: str
    issue_notes: Optional[str] = ""

class ComplaintResponse(BaseModel):
    complaint_id: int
    subject: str
    description: str
    status: str

@router.post("/complaints")
def submit_complaint(payload: ComplaintRequest, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT NVL(MAX(COMPLAINT_ID), 0) + 1 FROM COMPLAINTS"
        )
        complaint_id = cursor.fetchone()[0]

        description_parts = [
            f"Message context: {payload.message_context}"
        ]

        if payload.issue_notes:
            description_parts.append(f"Notes: {payload.issue_notes}")

        subject = payload.issue_type[:200]
        description = "\n".join(description_parts)[:1000]

        cursor.execute(
            """
            INSERT INTO COMPLAINTS
            (
                COMPLAINT_ID,
                C_ID,
                SUBJECT,
                DESCRIPTION,
                STATUS
            )
            VALUES
            (
                :1,
                :2,
                :3,
                :4,
                'OPEN'
            )
            """,
            (
                complaint_id,
                current_user,
                subject,
                description
            )
        )
        conn.commit()
        return {
            "status": "success",
            "message": "Complaint submitted successfully.",
            "complaint_id": complaint_id
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

@router.get("/complaints", response_model=List[ComplaintResponse])
def get_complaints(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            SELECT
                COMPLAINT_ID,
                SUBJECT,
                DESCRIPTION,
                STATUS
            FROM COMPLAINTS
            WHERE C_ID = :1
            ORDER BY COMPLAINT_ID DESC
            """,
            (current_user,)
        )
        rows = cursor.fetchall()
        
        complaints = []
        for row in rows:
            complaint_id, subject, description, stat = row
            complaints.append({
                "complaint_id": complaint_id,
                "subject": subject or "",
                "description": (
                    description.read()
                    if hasattr(description, "read")
                    else str(description or "")
                ),
                "status": stat
            })
            
        return complaints
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()
