from backend.rag.intent_classifier import classify_intent

from backend.rag.tools import (
    get_loan_balance,
    get_loan_details,
    get_emi_schedule,
    get_payment_history,
    get_account_details,
    get_customer_profile,
    get_complaint_status
)


def route_query(query: str, customer_id: int):

    intent = classify_intent(query)

    if intent == "loan_balance":
        return intent, get_loan_balance(customer_id)

    elif intent == "loan_details":
        return intent, get_loan_details(customer_id)

    elif intent == "emi":
        return intent, get_emi_schedule(customer_id)

    elif intent == "payment_history":
        return intent, get_payment_history(customer_id)

    elif intent == "account_details":
        return intent, get_account_details(customer_id)

    elif intent == "customer_profile":
        return intent, get_customer_profile(customer_id)

    elif intent == "complaint":
        return intent, get_complaint_status(customer_id)

    return "faq", None