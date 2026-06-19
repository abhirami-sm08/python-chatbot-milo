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

@router.get("/admin/complaints")

def complaint_dashboard():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

        status,

        COUNT(*)

        FROM complaints

        GROUP BY status

    """)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows

@router.get("/admin/customers")

def customer_dashboard():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

        COUNT(*)

        FROM customers

        WHERE status='ACTIVE'

    """)

    result = cursor.fetchone()

    cursor.close()

    conn.close()

    return {

        "active_customers": result[0]

    }

@router.get("/admin/chat-count")

def chat_count():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM chat_msgs

    """)

    result = cursor.fetchone()

    cursor.close()

    conn.close()

    return {

        "total_messages": result[0]

    }

@router.get("/admin/top-questions")

def top_questions():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

        msg_txt,

        COUNT(*)

        FROM chat_msgs

        WHERE sender='USER'

        GROUP BY msg_txt

        ORDER BY COUNT(*) DESC

        FETCH FIRST 10 ROWS ONLY

    """)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows