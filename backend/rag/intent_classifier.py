from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

INTENTS = {

    "account_details": [
        "account status",
        "account details",
        "my account",
        "account number",
        "branch code"
    ],

    "profile_details": [
        "my profile",
        "my details",
        "customer profile",
        "contact info",
        "email address",
        "phone number"
    ],

    "loan_details": [
        "loan details",
        "my loan",
        "loan type",
        "interest rate",
        "tenure",
        "principal amount"
    ],

    "loan_balance": [
        "loan balance",
        "remaining balance",
        "outstanding amount",
        "remaining loan",
        "balance amount",
        "loan status",
        "amount left",
        "pending amount",
        "due amount",
        "total due"
    ],

    "emi_schedule": [

        "emi schedule",
        "next emi",
        "emi details",
        "emi due",
        "upcoming emi",
        "installments",
        "payment schedule"

    ],

    "payment_history": [

        "payment history",
        "previous payments",
        "transactions",
        "paid emi",
        "payment details",
        "recent payments"

    ],

    "complaint_status": [

        "complaint status",
        "track complaint",
        "my complaint",
        "complaint progress",
        "ticket status"

    ],

    "faq": [

        "gold loan",
        "interest rate",
        "kyc",
        "eligibility",
        "documents",
        "branch",
        "customer support",
        "loan process"

    ]

}

intent_vectors = {}

for intent, examples in INTENTS.items():

    embeddings = model.encode(
        examples,
        normalize_embeddings=True
    )

    intent_vectors[intent] = np.mean(
        embeddings,
        axis=0
    )


def classify_intent(
    query: str
):

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    best_intent = "faq"
    best_score = -1

    for intent, vector in intent_vectors.items():

        similarity = np.dot(
            query_embedding,
            vector
        )

        if similarity > best_score:

            best_score = similarity
            best_intent = intent

    if best_score < 0.45:

        return "faq"

    return best_intent