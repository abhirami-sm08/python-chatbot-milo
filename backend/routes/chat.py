from fastapi import APIRouter, Depends
from backend.models.schemas import ChatRequest, ChatResponse
from backend.auth import get_current_user
from backend.rag.pipeline import run_milo_rag
from backend.database import get_db_connection

router = APIRouter()

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
    customer_id: int = Depends(get_current_user)
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

    save_chat_message(
        customer_id,
        "BOT",
        ai_response,
        "CHAT"
    )

    return {
        "response": ai_response
    }