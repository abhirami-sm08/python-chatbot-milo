from datetime import datetime


def format_sql_response(
    intent: str,
    data: str
):

    if not data:

        return (
            "No information was found."
        )

    if intent == "loan_balance":

        return (
            "📄 Loan Details\n\n"
            f"{data}"
        )

    elif intent == "emi_schedule":

        return (
            "💳 EMI Schedule\n\n"
            f"{data}"
        )

    elif intent == "payment_history":

        return (
            "💰 Payment History\n\n"
            f"{data}"
        )

    elif intent == "complaint_status":

        return (
            "📝 Complaint Status\n\n"
            f"{data}"
        )

    return data