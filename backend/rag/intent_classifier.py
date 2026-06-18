import re

SQL_INTENTS = {

    "loan_balance": [
        "loan balance",
        "outstanding balance",
        "remaining balance",
        "balance amount",
        "amount remaining",
        "pending balance",
        "balance left"
    ],

    "loan_details": [
        "my loan",
        "loan details",
        "loan status",
        "interest rate",
        "loan type",
        "principal",
        "tenure"
    ],

    "emi": [
        "emi",
        "installment",
        "due date",
        "next emi",
        "monthly payment",
        "repayment schedule"
    ],

    "payment_history": [
        "payment",
        "payment history",
        "transaction",
        "transactions",
        "paid amount",
        "recent payment"
    ],

    "account_details": [
        "account",
        "account details",
        "account number",
        "branch",
        "branch code",
        "account type"
    ],

    "customer_profile": [
        "profile",
        "customer details",
        "my details",
        "phone",
        "mobile",
        "email",
        "contact details"
    ],

    "complaint": [
        "complaint",
        "complaints",
        "ticket",
        "issue",
        "grievance"
    ]
}


GENERAL_PATTERNS = [

    "what is",
    "how to",
    "how do",
    "how can",
    "why",
    "benefits",
    "features",
    "advantages",
    "eligibility",
    "documents",
    "gold loan",
    "personal loan",
    "education loan",
    "home loan",
    "vehicle loan",
    "policy",
    "interest calculation",
    "processing fee"
]


def clean_query(query: str):

    query = query.lower()

    query = re.sub(
        r"[^\w\s]",
        "",
        query
    )

    return query.strip()


def classify_intent(query: str):

    query = clean_query(query)

    # ---------- SQL ----------

    for intent, keywords in SQL_INTENTS.items():

        for keyword in keywords:

            if keyword in query:

                return intent

    # ---------- Personal Query ----------

    if (
        "my " in query
        or "me " in query
    ):

        if "loan" in query:
            return "loan_details"

        if "balance" in query:
            return "loan_balance"

        if "emi" in query:
            return "emi"

        if "payment" in query:
            return "payment_history"

        if "account" in query:
            return "account_details"

        if "profile" in query:
            return "customer_profile"

        if "complaint" in query:
            return "complaint"

    # ---------- FAQ ----------

    for pattern in GENERAL_PATTERNS:

        if pattern in query:

            return "faq"

    return "faq"