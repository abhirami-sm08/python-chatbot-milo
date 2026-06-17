from backend.rag.tools import (
    get_loan_balance,
    get_emi_schedule,
    get_account_details,
    get_payment_history,
    get_complaint_status
)


def route_query(query: str, customer_id: int):

    q = query.lower()

    if any(word in q for word in ["loan", "balance", "principal", "interest"]):
        return get_loan_balance(customer_id)

    if any(word in q for word in ["emi", "installment", "due"]):
        return get_emi_schedule(customer_id)

    if any(word in q for word in ["account", "branch"]):
        return get_account_details(customer_id)

    if any(word in q for word in ["payment", "paid", "transaction"]):
        return get_payment_history(customer_id)

    if any(word in q for word in ["complaint", "issue", "ticket"]):
        return get_complaint_status(customer_id)

    return None