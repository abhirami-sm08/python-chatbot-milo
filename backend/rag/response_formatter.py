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
            "\U0001f4c4 Loan Details\n\n"
            f"{data}"
        )

    elif intent == "emi_schedule":

        return (
            "\U0001f4b3 EMI Schedule\n\n"
            f"{data}"
        )

    elif intent == "payment_history":

        return (
            "\U0001f4b0 Payment History\n\n"
            f"{data}"
        )

    elif intent == "complaint_status":

        return (
            "\U0001f4dd Complaint Status\n\n"
            f"{data}"
        )

    elif intent == "account_details":

        return (
            "\U0001f3e6 Account Details\n\n"
            f"{data}"
        )

    elif intent == "profile_details":

        return (
            "\U0001f464 Profile Details\n\n"
            f"{data}"
        )

    elif intent == "loan_details":

        return (
            "\U0001f4c4 Loan Details\n\n"
            f"{data}"
        )

    return data