from fastapi import APIRouter

from backend.database import get_db_connection

router = APIRouter()


@router.get("/admin/chats")

def all_chats():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            c.name,

            m.sender,

            m.msg_txt,

            m.timestamp

        FROM chat_msgs m

        JOIN customers c

        ON m.c_id=c.c_id

        ORDER BY m.timestamp DESC

    """)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows