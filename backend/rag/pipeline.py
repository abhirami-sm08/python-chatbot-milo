import os
import re

import requests

from backend.config import settings
from backend.rag.vector_store import LocalVectorStore
from backend.rag.intent_classifier import classify_intent
from backend.rag.router import route_query
from backend.rag.response_formatter import format_sql_response
from backend.rag.memory import get_chat_history

# -------------------------------------------------
# Ollama Generation
# -------------------------------------------------

def generate_content_with_ollama(messages, temperature=0.2, max_output_tokens=None, model=None):
    """
    Call local Ollama server to generate content using the chat endpoint.
    """
    if model is None:
        model = settings.OLLAMA_MODEL
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,  # Keep the model loaded in VRAM to prevent slow loading
        "options": {
            "temperature": temperature
        }
    }
    if max_output_tokens:
        payload["options"]["num_predict"] = max_output_tokens
        
    try:
        response = requests.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Create a dummy object to mimic the Gemini response structure
        class DummyResponse:
            def __init__(self, text):
                self.text = text
                
        return DummyResponse(data.get("message", {}).get("content", ""))
        
    except Exception as e:
        print(f"Ollama generation failed: {e}")
        raise e

# -------------------------------------------------
# Vector Store
# -------------------------------------------------

vector_store = LocalVectorStore()

vector_store.populate_from_file(
    "faq_docs/muthoot_policy.txt"
)


def run_milo_rag(
    user_query: str,
    customer_id: int | None
) -> str:

    # ---------------------------------------------
    # Step 1 : Previous Conversation
    # ---------------------------------------------

    history = ""
    if customer_id is not None:
        history = get_chat_history(
            customer_id,
            limit=8
        )

    # ---------------------------------------------
    # Step 2 : Rewrite Follow-up Question (SKIPPED FOR SPEED)
    # ---------------------------------------------

    rewritten_query = user_query
    # We skip the rewrite LLM call to save 5+ seconds of processing time.
    # The final prompt still receives the history, so the LLM can infer context.

    # ---------------------------------------------
    # Step 3 : Semantic Intent Detection
    # ---------------------------------------------

    intent = classify_intent(
        rewritten_query
    )

    # ---------------------------------------------
    # Step 4 : SQL Router
    # ---------------------------------------------

    structured_data = ""
    faq_required = True

    if customer_id is not None:
        structured_data, faq_required = route_query(
            intent,
            rewritten_query,
            customer_id
        )

    # ---------------------------------------------
    # Step 5 : SQL Only
    # ---------------------------------------------

    if structured_data and not faq_required:

        return format_sql_response(
            intent,
            structured_data
        )

    # ---------------------------------------------
    # Step 6 : FAQ Semantic Search
    # ---------------------------------------------

    faq_context = ""

    if faq_required:

        faq_context = vector_store.semantic_search(

            rewritten_query,

            top_k=3

        )

    # ---------------------------------------------
    # Step 7 : Build Prompt
    # ---------------------------------------------

    system_prompt = f"""You are Milo, the AI Assistant for Muthoot Fincorp.
You help customers with:
• Loan information
• EMI details
• Payment history
• Complaint status
• Gold loan policies
• Company procedures

RULES:
1. Answer extremely concisely. Use maximum 2-3 sentences.
2. If DATABASE information is provided, use it directly to give specific amounts, dates, and details.
3. If FAQ information is provided, use it to explain policies.
4. If the user asks for account-specific details but Database Information is empty, POLITELY ASK THEM TO LOG IN.
5. Do not invent information.
6. Decline unrelated questions politely."""

    user_message = f"""Conversation History:
{history}

Database Information:
{structured_data}

FAQ Information:
{faq_context}

Customer Question:
{rewritten_query}

Answer the customer question based on the provided information."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # ---------------------------------------------
    # Step 8 : Gemini Response
    # ---------------------------------------------

    try:

        response = generate_content_with_ollama(
            messages=messages,
            temperature=0.2,
            max_output_tokens=150
        )

        if (
            response is not None
            and response.text is not None
        ):

            return response.text.strip()

        return (
            "I'm sorry, I couldn't generate a response "
            "at the moment."
        )

    except Exception as e:

        print(f"Pipeline Error: {e}")

        return (
            "I'm sorry, I'm having trouble processing your request right now. "
            "Please try again in a moment."
        )