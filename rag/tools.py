from database import get_db_connection


def _format_money(value) -> str:
    return f"Rs. {float(value):,.2f}" if value is not None else "not available"


def _format_date(value) -> str:
    return value.strftime("%Y-%m-%d") if hasattr(value, "strftime") else str(value)


def query_customer_account_summary(customer_id: int) -> str:
    """Retrieve secured customer data from ACCOUNTS, LOANS, EMI_SCHEDULE, and PAYMENTS."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT A_NO, A_TYPE, BRANCH_CODE, A_STATUS
            FROM ACCOUNTS
            WHERE C_ID = :1
            ORDER BY A_ID
            """,
            (customer_id,),
        )
        accounts = cursor.fetchall()

        cursor.execute(
            """
            SELECT L_ID, L_TYPE, P_AMT, INTEREST_RATE, EMI_AMT, TENURE, START_DATE, STATUS
            FROM LOANS
            WHERE C_ID = :1
            ORDER BY START_DATE DESC NULLS LAST
            """,
            (customer_id,),
        )
        loans = cursor.fetchall()

        if not accounts and not loans:
            return "No account or loan records were found for the current customer."

        sections = []

        if accounts:
            account_lines = [
                f"Account {a_no} ({a_type}), branch {branch_code}, status {status}."
                for a_no, a_type, branch_code, status in accounts
            ]
            sections.append("Accounts: " + " ".join(account_lines))

        loan_lines = []
        for loan_id, loan_type, principal, rate, emi_amt, tenure, start_date, status in loans:
            cursor.execute(
                """
                SELECT EMI_NO, DUE_DATE, EMI_AMT, BALANCE, STATUS
                FROM EMI_SCHEDULE
                WHERE L_ID = :1
                  AND NVL(UPPER(STATUS), 'PENDING') = 'PENDING'
                ORDER BY DUE_DATE
                FETCH FIRST 1 ROWS ONLY
                """,
                (loan_id,),
            )
            emi = cursor.fetchone()
            emi_info = "No pending EMI found."
            if emi:
                emi_no, due_date, next_emi_amt, balance, _emi_status = emi
                emi_info = (
                    f"Next EMI #{emi_no} is {_format_money(next_emi_amt)} due on "
                    f"{_format_date(due_date)} with balance {_format_money(balance)}."
                )

            cursor.execute(
                """
                SELECT NVL(SUM(AMT_PAID), 0), MAX(PAYMENT_DATE)
                FROM PAYMENTS
                WHERE L_ID = :1
                  AND NVL(UPPER(STATUS), 'SUCCESS') IN ('SUCCESS', 'PAID', 'COMPLETED')
                """,
                (loan_id,),
            )
            total_paid, last_payment_date = cursor.fetchone()
            payment_info = f"Total paid is {_format_money(total_paid)}."
            if last_payment_date:
                payment_info += f" Last payment date was {_format_date(last_payment_date)}."

            start = _format_date(start_date) if start_date else "not available"
            loan_lines.append(
                f"Loan {loan_id}: {loan_type}, principal {_format_money(principal)}, "
                f"interest {rate}%, EMI {_format_money(emi_amt)}, tenure {tenure} months, "
                f"started {start}, status {status}. {emi_info} {payment_info}"
            )

        if loan_lines:
            sections.append("Loans: " + " ".join(loan_lines))

        return "\n".join(sections)
    except Exception as e:
        return f"Database reading exception encountered: {str(e)}"
    finally:
        cursor.close()
        conn.close()


def log_chat_message(customer_id: int, sender: str, message: str, intent_type: str | None = None) -> None:
    """Store a chat message in CHAT_MSGS."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NVL(MAX(M_ID), 0) + 1 FROM CHAT_MSGS")
        message_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO CHAT_MSGS (M_ID, C_ID, SENDER, MSG_TXT, TIMESTAMP, INTENT_TYPE)
            VALUES (:1, :2, :3, :4, SYSTIMESTAMP, :5)
            """,
            (message_id, customer_id, sender, message, intent_type),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Chat logging failure: {e}")
    finally:
        cursor.close()
        conn.close()


def create_customer_complaint(
    customer_id: int,
    subject: str,
    description: str,
    loan_id: int | None = None,
) -> int:
    """Create a customer complaint in COMPLAINTS and return its id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NVL(MAX(COMPLAINT_ID), 0) + 1 FROM COMPLAINTS")
        complaint_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO COMPLAINTS (COMPLAINT_ID, C_ID, L_ID, SUBJECT, DESCRIPTION, STATUS)
            VALUES (:1, :2, :3, :4, :5, 'OPEN')
            """,
            (complaint_id, customer_id, loan_id, subject, description),
        )
        conn.commit()
        return int(complaint_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
