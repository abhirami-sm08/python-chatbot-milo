from backend.rag.tools import *

SQL_INTENTS = {

    "loan_balance": get_loan_balance,

    "emi_schedule": get_emi_schedule,

    "payment_history": get_payment_history,

    "complaint_status": get_complaint_status,

    "account_details": get_account_details,

    "profile_details": get_customer_profile,

    "loan_details": get_loan_details

}


HYBRID_KEYWORDS = [

    "policy",

    "eligible",

    "eligibility",

    "why",

    "can",

    "should",

    "explain",

    "benefits",

    "documents",

    "interest",

    "gold loan",

    "preclose",

    "pre close",

    "foreclose"

]


def route_query(
    intent,
    user_query,
    customer_id
):

    sql_result = ""

    faq_required = False

    query = user_query.lower()

    # -----------------------------------------
    # EMI Intent
    # -----------------------------------------

    if intent == "emi_schedule":

        next_keywords = [

            "next",

            "due",

            "upcoming",

            "latest",

            "when",

            "remaining"

        ]

        if any(

            word in query

            for word in next_keywords

        ):

            sql_result = get_next_emi(
                customer_id
            )

        else:

            sql_result = get_emi_schedule(
                customer_id
            )

    # -----------------------------------------
    # Other SQL Intents
    # -----------------------------------------

    elif intent in SQL_INTENTS:

        sql_result = SQL_INTENTS[intent](
            customer_id
        )

    # -----------------------------------------
    # FAQ Detection
    # -----------------------------------------

    if any(

        word in query

        for word in HYBRID_KEYWORDS

    ):

        faq_required = True

    elif intent == "faq":

        faq_required = True

    return (

        sql_result,

        faq_required

    )