import os
from dotenv import load_dotenv
import google.generativeai as genai
from rag.vector_store import LocalVectorStore
from rag.tools import query_customer_account_summary

load_dotenv()

# Initialize localized text retrieval structures
v_store = LocalVectorStore()
_vector_store_ready = False

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def _ensure_vector_store_ready():
    global _vector_store_ready
    if not _vector_store_ready:
        v_store.populate_from_file("faq_docs/muthoot_policy.txt")
        _vector_store_ready = True


def run_milo_rag(user_query: str, customer_id: int) -> str:
    # 1. Pull Context via Semantic Vector Retrieval (Unstructured Policy Documents)
    _ensure_vector_store_ready()
    unstructured_context = v_store.semantic_search(user_query, top_k=2)
    
    # 2. Check Intent for Account-Specific Data (Structured SQL Data Retrieval)
    structured_context = ""
    account_keywords = [
        "account",
        "balance",
        "due date",
        "emi",
        "i owe",
        "loan",
        "outstanding",
        "paid",
        "payment",
        "status",
        "tenure",
    ]
    if any(kw in user_query.lower() for kw in account_keywords):
        structured_context = query_customer_account_summary(customer_id)
        
    # 3. Construct System Instructions with Augmented Context
    system_instruction = f"""
    You are Milo, an intelligent conversational bank teller assistant representing Muthoot Pappachan Technologies.
    Provide precise, polite assistance to user questions based strictly on the retrieved knowledge sources below.
    If you don't know the answer, ask them to check back with customer care lines.

    [Company Rules & FAQ Context Documentation]:
    {unstructured_context}

    [Live Secured Database Profile of Current Chat User]:
    {structured_context}
    """
    
    try:
        response = model.generate_content(
            [system_instruction, f"User Input Query: {user_query}"],
            request_options={"timeout": 30},
        )
        return response.text
    except Exception as e:
        return f"I'm experiencing an internal response generation issue right now. Error Details: {str(e)}"
