from database import get_db_connection

def query_customer_account_summary(customer_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                L_ID,
                L_TYPE,
                P_AMT,
                INTEREST_RATE,
                EMI_AMT
            FROM LOANS
            WHERE C_ID = :1
            AND STATUS = 'ACTIVE'
            """,
            (customer_id,)
        )

        loan = cursor.fetchone()

        if not loan:
            return "No active loan found."

        loan_id, loan_type, principal, rate, emi_amount = loan

        cursor.execute(
            """
            SELECT
                EMI_NO,
                DUE_DATE,
                EMI_AMT,
                BALANCE,
                STATUS
            FROM EMI_SCHEDULE
            WHERE L_ID = :1
            ORDER BY EMI_NO
            """,
            (loan_id,)
        )

        emi = cursor.fetchone()

        if emi:

            emi_no, due_date, emi_amt, balance, emi_status = emi

            return (
                f"Loan Type: {loan_type}. "
                f"Principal: ₹{principal}. "
                f"Interest: {rate}%. "
                f"EMI: ₹{emi_amount}. "
                f"Next EMI #{emi_no} due on {due_date}. "
                f"Remaining Balance ₹{balance}. "
                f"Status: {emi_status}"
            )

        return (
            f"Loan Type: {loan_type}. "
            f"Principal: ₹{principal}. "
            f"Interest: {rate}%."
        )

    finally:

        cursor.close()
        conn.close()