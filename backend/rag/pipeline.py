import os

from dotenv import load_dotenv
from google import genai

from backend.rag.vector_store import LocalVectorStore
from backend.rag.router import route_query
from backend.rag.prompts import (
    SYSTEM_PROMPT,
    SQL_PROMPT,
    FAQ_PROMPT
)
from backend.rag.memory import (
    add_message,
    get_history
)

load_dotenv()

# ----------------------------
# Gemini Configuration
# ----------------------------

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ----------------------------
# Load Vector Store
# ----------------------------

v_store = LocalVectorStore()

v_store.populate_from_file(
    "faq_docs/muthoot_policy.txt"
)

# ----------------------------
# Gemini Response
# ----------------------------

def generate_response(prompt: str):

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return (
            "Unable to generate response.\n"
            f"Error: {str(e)}"
        )

# ----------------------------
# Main RAG Pipeline
# ----------------------------

def run_milo_rag(
    user_query: str,
    customer_id: int
):

    # Get previous conversation

    history = get_history(
        customer_id
    )

    # Detect Intent

    intent, structured_context = route_query(
        user_query,
        customer_id
    )

    # ======================================================
    # SQL QUERIES
    # ======================================================

    if intent != "faq":

        prompt = SQL_PROMPT.format(

            system=SYSTEM_PROMPT,

            context=f"""
Conversation History:

{history}

Database Result:

{structured_context}
""",

            question=user_query
        )

        response = generate_response(
            prompt
        )

        add_message(
            customer_id,
            "User",
            user_query
        )

        add_message(
            customer_id,
            "Milo",
            response
        )

        return response

    # ======================================================
    # FAQ + RAG
    # ======================================================

    faq_context = v_store.semantic_search(
        user_query,
        top_k=3
    )

    prompt = FAQ_PROMPT.format(

        system=SYSTEM_PROMPT,

        context=f"""
Conversation History:

{history}

Knowledge Base:

{faq_context}
""",

        question=user_query
    )

    response = generate_response(
        prompt
    )

    add_message(
        customer_id,
        "User",
        user_query
    )

    add_message(
        customer_id,
        "Milo",
        response
    )

    return response