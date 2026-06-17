import os
from dotenv import load_dotenv
from google import genai

from backend.rag.vector_store import LocalVectorStore
from backend.rag.tools import query_customer_account_summary

load_dotenv()

# Gemini Setup
client=genai.Client(
    api_key=os.getenv("AQ.Ab8RN6JwbYSoZxAoqLZZtzk9bzJ-RGliKxUYW-kW7wfRWeS5UQ")
)

model = client.models


# Load Vector Store
v_store = LocalVectorStore()
v_store.populate_from_file(
    "faq_docs/muthoot_policy.txt"
)

ACCOUNT_KEYWORDS = [
    "loan",
    "my loan",
    "emi",
    "my emi",
    "balance",
    "outstanding",
    "payment",
    "due date",
    "remaining amount",
    "loan status"
]

def run_milo_rag(
    user_query: str,
    customer_id: int
) -> str:

    # Vector Search
    unstructured_context = v_store.semantic_search(
        user_query,
        top_k=2
    )

    # SQL Context
    structured_context = ""

    if any(
        keyword in user_query.lower()
        for keyword in ACCOUNT_KEYWORDS
    ):
        structured_context = (
            query_customer_account_summary(
                customer_id
            )
        )

    prompt = f"""
You are Milo, the AI assistant for Muthoot Fincorp.

Rules:
1. Answer politely and professionally.
2. Use SQL data when available.
3. Use FAQ context for company policy questions.
4. Never invent loan details.
5. If information is unavailable, advise contacting customer support.

DATABASE CONTEXT:
{structured_context}

FAQ CONTEXT:
{unstructured_context}

USER QUESTION:
{user_query}
"""

try:
       response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
      )
      text = response.text          # ✅ must be inside try

except Exception as e:
      return (
        "Unable to generate response. "
        f"Error: {str(e)}"
    )