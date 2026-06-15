__all__ = [
    "LocalVectorStore",
    "create_customer_complaint",
    "log_chat_message",
    "query_customer_account_summary",
    "run_milo_rag",
]


def __getattr__(name):
    if name == "LocalVectorStore":
        from .vector_store import LocalVectorStore

        return LocalVectorStore
    if name == "query_customer_account_summary":
        from .tools import query_customer_account_summary

        return query_customer_account_summary
    if name == "log_chat_message":
        from .tools import log_chat_message

        return log_chat_message
    if name == "create_customer_complaint":
        from .tools import create_customer_complaint

        return create_customer_complaint
    if name == "run_milo_rag":
        from .pipeline import run_milo_rag

        return run_milo_rag
    raise AttributeError(f"module 'rag' has no attribute {name!r}")
