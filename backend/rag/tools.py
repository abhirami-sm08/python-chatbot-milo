from backend.database import get_db_connection


def get_account_details(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            A_NO,
            A_TYPE,
            BRANCH_CODE,
            A_STATUS
        FROM ACCOUNTS
        WHERE C_ID = :1
    """, (customer_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return "No account found."

    return f"""
Account Number : {row[0]}
Account Type   : {row[1]}
Branch Code    : {row[2]}
Status         : {row[3]}
"""

def get_customer_profile(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            NAME,
            PHONE,
            EMAIL,
            STATUS
        FROM CUSTOMERS
        WHERE C_ID = :1
    """, (customer_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return "Customer not found."

    return f"""
Name    : {row[0]}
Phone   : {row[1]}
Email   : {row[2]}
Status  : {row[3]}
"""


def get_loan_details(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            L_ID,
            L_TYPE,
            P_AMT,
            INTEREST_RATE,
            EMI_AMT,
            TENURE,
            STATUS
        FROM LOANS
        WHERE C_ID = :1
    """, (customer_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return "No loan found."

    return f"""
Loan ID        : {row[0]}
Loan Type      : {row[1]}
Principal      : ₹{row[2]:,.2f}
Interest Rate  : {row[3]}%
Monthly EMI    : ₹{row[4]:,.2f}
Tenure         : {row[5]} months
Status         : {row[6]}
"""


def get_loan_balance(customer_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
        SELECT e.BALANCE
        FROM EMI_SCHEDULE e
        JOIN LOANS l
        ON e.L_ID = l.L_ID
        WHERE l.C_ID = :1
        ORDER BY e.EMI_NO DESC
        FETCH FIRST 1 ROW ONLY
        """, (customer_id,))

        row = cursor.fetchone()

        if not row:
            return "No active loan found."

        return f"Your current loan balance is: ₹{row[0]:,.2f}"  

    finally:
        cursor.close()
        conn.close()

def get_emi_schedule(customer_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
    SELECT
        e.EMI_NO,
        e.DUE_DATE,
        e.EMI_AMT,
        e.STATUS
    FROM EMI_SCHEDULE e
    JOIN LOANS l
        ON e.L_ID = l.L_ID
    WHERE l.C_ID = :1
    ORDER BY e.EMI_NO
""", (customer_id,))

        rows = cursor.fetchall()

        if not rows:
            return "No EMI schedule found."

        result = "EMI Schedule:\n\n"

        for emi_no, due_date, amount, status in rows:
            result += (
                f"EMI #{emi_no}\n"
                f"Due Date : {due_date}\n"
                f"Amount   : ₹{amount:,.2f}\n"
                f"Status   : {status}\n\n"
            )

        return result

    finally:
        cursor.close()
        conn.close()

def get_payment_history(customer_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                p.AMT_PAID,
                p.PAYMENT_DATE,
                p.STATUS
            FROM PAYMENTS p
            JOIN LOANS l
                ON p.L_ID = l.L_ID
            WHERE l.C_ID = :1
            ORDER BY p.PAYMENT_DATE DESC
        """, (customer_id,))

        rows = cursor.fetchall()

        if not rows:
            return "No payment history found."

        result = ""

        for amount, date, status in rows:

            result += (
                f"Amount : ₹{amount:,.2f}\n"
                f"Date   : {date}\n"
                f"Status : {status}\n\n"
            )

        return result

    finally:
        cursor.close()
        conn.close()

def get_complaint_status(customer_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                SUBJECT,
                STATUS
            FROM COMPLAINTS
            WHERE C_ID = :1
            ORDER BY COMPLAINT_ID DESC
        """, (customer_id,))

        rows = cursor.fetchall()

        if not rows:
            return "No complaints found."

        result = ""

        for subject, status in rows:

            result += (
                f"Complaint : {subject}\n"
                f"Status    : {status}\n\n"
            )

        return result

    finally:
        cursor.close()
        conn.close()