from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter()


@router.get("/admin/analytics")

def analytics():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total Customers
    cursor.execute("""
        SELECT COUNT(*)
        FROM CUSTOMERS
    """)
    total_customers = cursor.fetchone()[0]

    # Total Loans
    cursor.execute("""
        SELECT COUNT(*)
        FROM LOANS
    """)
    total_loans = cursor.fetchone()[0]

    # Active Loans
    cursor.execute("""
        SELECT COUNT(*)
        FROM LOANS
        WHERE STATUS='ACTIVE'
    """)
    active_loans = cursor.fetchone()[0]

    # Total Chats
    cursor.execute("""
        SELECT COUNT(*)
        FROM CHAT_MSGS
    """)
    total_messages = cursor.fetchone()[0]

    # Complaints
    cursor.execute("""
        SELECT COUNT(*)
        FROM COMPLAINTS
    """)
    complaints = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {

        "customers": total_customers,

        "loans": total_loans,

        "active_loans": active_loans,

        "messages": total_messages,

        "complaints": complaints

    }

@router.get("/admin/loan-summary")

def loan_summary():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            L_TYPE,

            COUNT(*)

        FROM LOANS

        GROUP BY L_TYPE

    """)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows

@router.get("/admin/complaint-summary")

def complaint_summary():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            STATUS,

            COUNT(*)

        FROM COMPLAINTS

        GROUP BY STATUS

    """)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows

@router.get("/admin/chat-daily")

def chat_daily():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            TRUNC(TIMESTAMP),

            COUNT(*)

        FROM CHAT_MSGS

        GROUP BY TRUNC(TIMESTAMP)

        ORDER BY TRUNC(TIMESTAMP)

    """)

    rows = cursor.fetchall()

    cursor.close()

    conn.close()

    return rows