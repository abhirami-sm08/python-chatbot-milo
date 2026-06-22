from backend.database import get_db_connection


def get_chat_history(customer_id, limit=8):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
    SENDER,
    MSG_TXT
FROM CHAT_MSGS
WHERE C_ID = :1
ORDER BY TIMESTAMP DESC
FETCH FIRST :2 ROWS ONLY
    """, [customer_id, limit])

    rows = cursor.fetchall()
    rows.reverse()

    history = ""

    for sender, message in rows:
        if hasattr(message, "read"):
            message = message.read()
        history += f"{sender}: {message}\n"

    cursor.close()
    conn.close()

    return history