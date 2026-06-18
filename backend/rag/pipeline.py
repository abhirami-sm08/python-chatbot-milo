import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.rag.vector_store import LocalVectorStore
from backend.rag.intent_classifier import classify_intent
from backend.rag.router import route_query
from backend.rag.response_formatter import format_sql_response
from backend.rag.memory import get_chat_history

load_dotenv()

# -------------------------------------------------
# Gemini Client
# -------------------------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -------------------------------------------------
# Vector Store
# -------------------------------------------------

vector_store = LocalVectorStore()

vector_store.populate_from_file(
    "faq_docs/muthoot_policy.txt"
)


def run_milo_rag(
    user_query: str,
    customer_id: int
) -> str:

    # ---------------------------------------------
    # Step 1 : Semantic Intent Detection
    # ---------------------------------------------

    intent = classify_intent(
        user_query
    )

    # ---------------------------------------------
    # Step 2 : Previous Conversation
    # ---------------------------------------------

    history = get_chat_history(
        customer_id,
        limit=8
    )

    # ---------------------------------------------
    # Step 3 : SQL Router
    # ---------------------------------------------

    structured_data, faq_required = route_query(
        intent,
        user_query,
        customer_id
    )

    # ---------------------------------------------
    # Step 4 : SQL Only
    # ---------------------------------------------

    if structured_data and not faq_required:

        return format_sql_response(
            intent,
            structured_data
        )

    # ---------------------------------------------
    # Step 5 : FAQ Semantic Search
    # ---------------------------------------------

    faq_context = ""

    if faq_required:

        faq_context = vector_store.semantic_search(
            user_query,
            top_k=3
        )

    # ---------------------------------------------
    # Step 6 : Prompt
    # ---------------------------------------------

    prompt = f"""
You are Milo, the AI Assistant for Muthoot Fincorp.

You help customers regarding loans, EMI, complaints,
payments and company policies.

RULES

1. Continue the conversation naturally.

2. Use DATABASE information whenever available.

3. DATABASE information is always correct.

4. FAQ information should only be used for explaining
company policies, eligibility, documents, interest,
gold loans and procedures.

5. Never invent customer information.

6. If DATABASE and FAQ are both available,
combine them into one natural answer.

7. If information is unavailable,
politely ask the customer to contact
Muthoot Fincorp Customer Support.

----------------------------------------

Conversation History

{history}

----------------------------------------

Database Information

{structured_data}

----------------------------------------

FAQ Information

{faq_context}

----------------------------------------

Customer Question

{user_query}

----------------------------------------

Answer as Milo.
"""

    # ---------------------------------------------
    # Step 7 : Gemini
    # ---------------------------------------------

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.2,

                max_output_tokens=500

            )

        )

        return response.text

    except Exception as e:

        return (
            "Unable to generate response.\n"
            f"Error: {str(e)}"
        )