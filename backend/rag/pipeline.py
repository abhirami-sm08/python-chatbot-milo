import os
import re
from google import genai
from google.genai import types

from backend.config import settings
from backend.rag.vector_store import LocalVectorStore
from backend.rag.intent_classifier import classify_intent
from backend.rag.router import route_query
from backend.rag.response_formatter import format_sql_response
from backend.rag.memory import get_chat_history

# -------------------------------------------------
# API Key Rotation & Fallback Loading
# -------------------------------------------------

def load_all_api_keys() -> list[str]:
    keys = []
    # Try reading from api.txt in the backend parent directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_txt_path = os.path.join(base_dir, "api.txt")
    if os.path.exists(api_txt_path):
        try:
            with open(api_txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    # Match clean AQ. key format
                    m = re.match(r"^(AQ\.[a-zA-Z0-9_-]+)", line.strip())
                    if m:
                        keys.append(m.group(1))
        except Exception as e:
            print(f"Error loading api.txt: {e}")
    
    # Prepend the primary key from settings if present and unique
    primary = settings.GEMINI_API_KEY
    if primary and primary not in keys:
        keys.insert(0, primary)
    return keys

API_KEYS = load_all_api_keys()
current_key_idx = 0

def generate_content_with_fallback(contents, config, model="gemini-2.5-flash"):
    """
    Attempt to call Gemini generate_content using primary key and rotates through 
    available fallback keys from api.txt if rate limits or quota exceptions occur.
    Remembers the last successful key index to speed up future requests.
    """
    global current_key_idx
    last_ex = None
    n_keys = len(API_KEYS)
    for i in range(n_keys):
        idx = (current_key_idx + i) % n_keys
        key = API_KEYS[idx]
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            # Save the successful key index
            current_key_idx = idx
            return response
        except Exception as e:
            print(f"Gemini key index {idx} failed: {e}")
            last_ex = e
    if last_ex:
        raise last_ex
    raise Exception("No valid Gemini API keys found.")

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
    # Step 2 : Rewrite Follow-up Question
    # ---------------------------------------------

    rewritten_query = user_query
    # Only rewrite if there is actual history to reference
    if history.strip():
        try:

            rewrite_prompt = f"""
You are an AI assistant that rewrites follow-up customer questions into complete standalone questions.

Conversation History:

{history}

Current Customer Question:

{user_query}

Instructions:

- Use the conversation history.
- Rewrite the current question into a complete standalone question.
- If the question already makes sense, return it unchanged.
- Never answer the question.
- Return ONLY the rewritten question.

Examples:

Conversation:

User: Show my EMI schedule.

User: When is the next one due?

Output:
When is my next EMI due?

-----------------------------------

Conversation:

User: Tell me about my loan.

User: How much is left?

Output:
What is my remaining loan balance?

-----------------------------------

Conversation:

User: Show my payment history.

User: Which payment was the latest?

Output:
Show my latest payment history.

-----------------------------------

Conversation:

User: I raised a complaint yesterday.

User: What's its status?

Output:
What is the status of my complaint?

"""

            rewrite_response = generate_content_with_fallback(
                model="gemini-2.5-flash",
                contents=rewrite_prompt,
                config=types.GenerateContentConfig(
                    temperature=0
                )
            )

            rewritten_query = rewrite_response.text.strip()

        except Exception as e:
            print(f"Rewrite Exception: {e}")
            rewritten_query = user_query

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

    prompt = f"""
You are Milo, the AI Assistant for Muthoot Fincorp.

You help customers with:

• Loan information
• EMI details
• Payment history
• Complaint status
• Gold loan policies
• Company procedures

==================================================

RULES

1. Continue the conversation naturally.

2. Always use DATABASE information whenever available.

3. DATABASE information is always correct. You have full access to the user's secure database information. Answer their questions directly and provide specific amounts, dates, and details using this data without citing privacy or security concerns.

4. FAQ information should only explain company policies, eligibility, documents, gold loans, repayment methods, interest rates and procedures.

5. Never invent customer information.

6. If the user asks for account-specific details (like loan balance, EMI, or account status) but the Database Information is empty, POLITELY ASK THEM TO LOG IN to view their secure account details. Do not tell them to contact customer support for this.

7. OUT OF DOMAIN: If the customer's question is entirely unrelated to finance, banking, Muthoot Fincorp, or loans (e.g., asking for a poem, sports scores, cooking recipes), politely decline to answer and remind them you are a banking assistant.

8. If both DATABASE and FAQ information are available, combine both into one natural answer.

==================================================

Conversation History

{history}

==================================================

Database Information

{structured_data}

==================================================

FAQ Information

{faq_context}

==================================================

Customer Question

{rewritten_query}

==================================================

Answer as Milo in a professional,
friendly and concise manner.
"""
    
    # ---------------------------------------------
    # Step 8 : Gemini Response
    # ---------------------------------------------

    try:

        response = generate_content_with_fallback(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=500
            )
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