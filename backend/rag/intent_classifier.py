from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    local_files_only=True
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
        "loan bal",
        "lown bal",
        "loan baal",
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
        "loan process",
        "loan schemes",
        "loan schemas",
        "available schemes",
        "available schemas"

    ]

}

intent_vectors = {}

for intent, examples in INTENTS.items():

    embeddings = model.encode(
        examples,
        normalize_embeddings=True
    )

    intent_vectors[intent] = embeddings


def classify_intent(
    query: str
):

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    )

    best_intent = "faq"
    best_score = -1

    for intent, vectors in intent_vectors.items():

        similarities = np.dot(
            vectors,
            query_embedding
        )
        max_sim = np.max(similarities)

        if max_sim > best_score:

            best_score = max_sim
            best_intent = intent

    if best_score < 0.5:

        return "faq"

    return best_intent