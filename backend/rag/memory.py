from backend.database import get_db_connection


def get_chat_history(
    customer_id: int,
    limit: int = 10
):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT sender,
               msg_txt
        FROM chat_msgs
        WHERE c_id = :1
        ORDER BY timestamp DESC
        FETCH FIRST :2 ROWS ONLY
        """,
        (
            customer_id,
            limit
        )
    )

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    rows.reverse()

    history = ""

    for sender, message in rows:

        history += f"{sender}: {message}\n"

    return history