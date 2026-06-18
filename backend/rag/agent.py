from backend.rag.tools import (
    get_loan_balance,
    get_emi_schedule,
    get_payment_history,
    get_complaint_status
)

TOOLS = {
    "loan_balance": get_loan_balance,
    "emi_schedule": get_emi_schedule,
    "payment_history": get_payment_history,
    "complaint_status": get_complaint_status
}


def execute_tools(intents, customer_id):

    results = {}

    for intent in intents:

        tool = TOOLS.get(intent)

        if tool is None:
            continue

        try:

            output = tool(customer_id)

            if output:
                results[intent] = output

        except Exception as e:

            print(f"{intent} failed:", e)

    return results