from backend.rag.tools import *

SQL_INTENTS = {

    "loan_balance": get_loan_balance,

    "emi_schedule": get_emi_schedule,

    "payment_history": get_payment_history,

    "complaint_status": get_complaint_status

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

    if intent in SQL_INTENTS:

        sql_result = SQL_INTENTS[intent](customer_id)

    query = user_query.lower()

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