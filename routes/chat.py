from fastapi import APIRouter, Depends

from auth import get_current_user
from models.schemas import ChatRequest, ChatResponse, ComplaintRequest, ComplaintResponse
from rag.pipeline import run_milo_rag
from rag.tools import create_customer_complaint, log_chat_message

router = APIRouter(tags=["chat"])

SENSITIVE_WORDS = ["password", "pin", "otp", "cvv"]


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, customer_id: int = Depends(get_current_user)):
    user_msg = payload.message

    if any(word in user_msg.lower() for word in SENSITIVE_WORDS):
        log_chat_message(customer_id, "USER", "[Sensitive message blocked]", "SECURITY")
        return {
            "response": "For identity protection, do not share passwords, PINs, OTPs, or CVV details in conversation threads."
        }

    log_chat_message(customer_id, "USER", user_msg, "CHAT")
    ai_answer = run_milo_rag(user_msg, customer_id)
    log_chat_message(customer_id, "MILO", ai_answer, "CHAT")
    return {"response": ai_answer}


@router.post("/complaints", response_model=ComplaintResponse)
def complaint_endpoint(
    payload: ComplaintRequest,
    customer_id: int = Depends(get_current_user),
):
    complaint_id = create_customer_complaint(
        customer_id=customer_id,
        subject=payload.subject,
        description=payload.description,
        loan_id=payload.loan_id,
    )
    return {
        "complaint_id": complaint_id,
        "status": "OPEN",
        "message": "Complaint registered successfully.",
    }
