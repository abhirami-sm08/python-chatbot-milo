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