import re
import json
from typing import Generator
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from backend.models.schemas import ChatRequest, ChatResponse
from backend.auth import get_optional_user
from backend.rag.pipeline import run_milo_rag, run_milo_rag_stream
from backend.database import get_db_connection

router = APIRouter()

# ─── Curated FAQ suggestion list ───────────────────────────────────────────────
FAQ_SUGGESTIONS = [
    "What is a gold loan?",
    "How much loan can I get against gold?",
    "What is the interest rate for gold loan?",
    "What documents are required for gold loan?",
    "Who is eligible for a gold loan?",
    "What gold purity is accepted?",
    "How can I repay my loan?",
    "Can I pay my EMI online?",
    "What is my outstanding balance?",
    "What is my EMI amount?",
    "When is my next EMI due date?",
    "Show my active loans.",
    "Show my payment history.",
    "What is KYC and is it mandatory?",
    "Which ID proof is accepted?",
    "Is PAN card mandatory?",
    "Can I repay early?",
    "What happens if I miss an EMI?",
    "How do I close my loan?",
    "What is LTV ratio?",
    "Does Muthoot Fincorp offer personal loans?",
    "What is a business loan?",
    "Does Muthoot offer insurance?",
    "How to apply for a gold loan?",
    "Can I pledge gold coins?",
    "Is Aadhaar accepted as proof?",
    "What are the repayment options?",
    "How long does gold loan approval take?",
    "What is Muthoot Fincorp?",
    "Is Muthoot FinCorp RBI regulated?",
    "How many branches does Muthoot have?",
    "Can homemakers apply for a gold loan?",
    "Can students apply for a gold loan?",
    "What is the maximum loan tenure?",
    "What schemes are available for gold loans?",
    "How to check my loan status?",
    "How to update my contact details?",
    "What is the processing fee?",
    "Can I get a top-up on my gold loan?",
    "How is gold valuation done?",
]

SENSITIVE_WORDS = [
    "password",
    "pin",
    "otp",
    "cvv"
]

def save_chat_message(
    customer_id,
    sender,
    message,
    intent_type="GENERAL"
):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO CHAT_MSGS
            (
                M_ID,
                C_ID,
                SENDER,
                MSG_TXT,
                TIMESTAMP,
                INTENT_TYPE
            )
            VALUES
            (
                CHAT_SEQ.NEXTVAL,
                :1,
                :2,
                :3,
                SYSTIMESTAMP,
                :4
            )
            """,
            (
                customer_id,
                sender,
                message,
                intent_type
            )
        )

        conn.commit()

    finally:

        cursor.close()
        conn.close()


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat_endpoint(
    payload: ChatRequest,
    customer_id: int | None = Depends(get_optional_user)
):

    user_message = payload.message

    if any(
        word in user_message.lower()
        for word in SENSITIVE_WORDS
    ):

        return {
            "response":
            "For security reasons, never share passwords, PINs, OTPs or CVV numbers."
        }

    if customer_id is not None:
        save_chat_message(
            customer_id,
            "USER",
            user_message,
            "CHAT"
        )

    ai_response = run_milo_rag(
        user_message,
        customer_id
    )

    if customer_id is not None:
        save_chat_message(
            customer_id,
            "BOT",
            ai_response,
            "CHAT"
        )

    return {
        "response": ai_response
    }


# ─── Suggest endpoint ──────────────────────────────────────────────────────────
@router.get("/suggest")
def suggest_endpoint(
    q: str = Query(default="", max_length=200)
):
    """
    Return up to 5 FAQ suggestions whose text contains the query string
    (case-insensitive). Used by the frontend typing suggestions dropdown.
    """
    q = q.strip()
    if not q or len(q) < 2:
        return {"suggestions": []}

    q_lower = q.lower()
    matches = [
        s for s in FAQ_SUGGESTIONS
        if q_lower in s.lower()
    ][:5]

    return {"suggestions": matches}


# ─── Streaming chat endpoint ───────────────────────────────────────────────────
@router.post("/chat/stream")
def chat_stream_endpoint(
    payload: ChatRequest,
    customer_id: int | None = Depends(get_optional_user)
):
    """
    Run the RAG pipeline and stream the response sentence-by-sentence
    via Server-Sent Events so the browser can render it progressively.
    """
    user_message = payload.message

    if any(word in user_message.lower() for word in SENSITIVE_WORDS):
        def _security_stream():
            msg = "For security reasons, never share passwords, PINs, OTPs or CVV numbers."
            yield f"data: {json.dumps({'chunk': msg})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        return StreamingResponse(_security_stream(), media_type="text/event-stream")

    if customer_id is not None:
        save_chat_message(customer_id, "USER", user_message, "CHAT")

    def _stream_response() -> Generator:
        full_text = ""
        for token in run_milo_rag_stream(user_message, customer_id):
            full_text += token
            yield f"data: {json.dumps({'chunk': token})}\n\n"
        
        yield f"data: {json.dumps({'done': True, 'full': full_text})}\n\n"

        if customer_id is not None:
            save_chat_message(customer_id, "BOT", full_text, "CHAT")

    return StreamingResponse(
        _stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )