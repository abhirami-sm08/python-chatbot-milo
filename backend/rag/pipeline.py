from functools import lru_cache
from backend.llm import generate_chat_response, generate_chat_response_stream
from backend.rag.vector_store import LocalVectorStore
from backend.rag.intent_classifier import classify_intent
from backend.rag.router import route_query
from backend.rag.response_formatter import format_sql_response
from backend.rag.memory import get_chat_history

# Simple in-memory cache for FAQ responses (no DB access needed)
_faq_cache: dict = {}

# -------------------------------------------------
# LLM Generation
# -------------------------------------------------

def generate_content(messages, temperature=0.2, max_output_tokens=None, model=None):
    """
    Call the configured LLM provider and return an object with a .text field.
    """
    try:
        return generate_chat_response(
            messages=messages,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            model=model
        )

    except Exception as e:
        print(f"LLM generation failed: {e}")
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

    if customer_id is not None:
        auth_rule = (
            "4. The user is CURRENTLY LOGGED IN. DO NOT ask them to log in. "
            "If the user asks for account-specific details but Database Information is empty, "
            "inform them that no relevant records were found in their account."
        )
    else:
        auth_rule = "4. If the user asks for account-specific details but Database Information is empty, POLITELY ASK THEM TO LOG IN."

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
{auth_rule}
5. Do not invent information.
6. Decline unrelated questions politely.
7. NEVER mention "the database", "the FAQ", or "the provided information" in your response. Speak naturally as Milo. If you don't know the answer, just say you don't have that information and suggest contacting support."""

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
    
    # ─────────────────────────────────────────────
    # Step 8 : LLM Response (with FAQ cache)
    # ─────────────────────────────────────────────

    # Cache key: only cache FAQ-only queries (no personal DB data)
    cache_key = None
    if not structured_data and faq_required:
        cache_key = rewritten_query.lower().strip()
        if cache_key in _faq_cache:
            return _faq_cache[cache_key]

    try:

        response = generate_content(
            messages=messages,
            temperature=0.1,
            max_output_tokens=120
        )

        if (
            response is not None
            and response.text is not None
        ):
            result = response.text.strip()
            # Store in FAQ cache if applicable
            if cache_key:
                if len(_faq_cache) > 256:
                    # Evict oldest entry
                    _faq_cache.pop(next(iter(_faq_cache)))
                _faq_cache[cache_key] = result
            return result

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


def run_milo_rag_stream(
    user_query: str,
    customer_id: int | None
):
    """
    Same pipeline as run_milo_rag but yields LLM tokens live.
    Steps 1-7 run normally (fast), only Step 8 streams.
    """
    history = ""
    if customer_id is not None:
        history = get_chat_history(customer_id, limit=8)

    rewritten_query = user_query
    intent = classify_intent(rewritten_query)

    structured_data = ""
    faq_required = True

    if customer_id is not None:
        structured_data, faq_required = route_query(intent, rewritten_query, customer_id)

    if structured_data and not faq_required:
        yield format_sql_response(intent, structured_data)
        return

    faq_context = ""
    if faq_required:
        faq_context = vector_store.semantic_search(rewritten_query, top_k=3)

    cache_key = None
    if not structured_data and faq_required:
        cache_key = rewritten_query.lower().strip()
        if cache_key in _faq_cache:
            yield _faq_cache[cache_key]
            return

    if customer_id is not None:
        auth_rule = (
            "4. The user is CURRENTLY LOGGED IN. DO NOT ask them to log in. "
            "If the user asks for account-specific details but Database Information is empty, "
            "inform them that no relevant records were found in their account."
        )
    else:
        auth_rule = "4. If the user asks for account-specific details but Database Information is empty, POLITELY ASK THEM TO LOG IN."

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
{auth_rule}
5. Do not invent information.
6. Decline unrelated questions politely.
7. NEVER mention "the database", "the FAQ", or "the provided information" in your response. Speak naturally as Milo. If you don't know the answer, just say you don't have that information and suggest contacting support."""

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

    full_text = ""
    try:
        for token in generate_chat_response_stream(messages, temperature=0.1, max_output_tokens=120):
            full_text += token
            yield token

        if cache_key and full_text:
            if len(_faq_cache) > 256:
                _faq_cache.pop(next(iter(_faq_cache)))
            _faq_cache[cache_key] = full_text

    except Exception as e:
        print(f"Stream pipeline error: {e}")
        yield "I'm sorry, I'm having trouble right now. Please try again."
