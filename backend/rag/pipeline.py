import os
from dotenv import load_dotenv
import google.generativeai as genai

from backend.rag.vector_store import LocalVectorStore
from backend.rag.router import route_query

load_dotenv()

# Gemini Setup
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

# Load Vector Store
v_store = LocalVectorStore()
v_store.populate_from_file("faq_docs/muthoot_policy.txt")


def run_milo_rag(
    user_query: str,
    customer_id: int
) -> str:

    # Retrieve FAQ context
    unstructured_context = v_store.semantic_search(
        user_query,
        top_k=2
    )

    # Retrieve structured Oracle data
    structured_context = route_query(
        user_query,
        customer_id
    )

    if structured_context is None:
        structured_context = ""

    prompt = f"""
You are Milo, the AI assistant for Muthoot Fincorp.

Instructions:
- Answer professionally.
- Use DATABASE CONTEXT whenever it is available.
- Use FAQ CONTEXT for policy and general questions.
- Never make up customer data.
- If information is unavailable, ask the customer to contact Muthoot customer support.

DATABASE CONTEXT:
{structured_context}

FAQ CONTEXT:
{unstructured_context}

USER QUESTION:
{user_query}
"""

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return (
            "Unable to generate response.\n"
            f"Error: {str(e)}"
        )