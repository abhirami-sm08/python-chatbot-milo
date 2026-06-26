import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:

    # -------------------------
    # Oracle Database
    # -------------------------

    DB_USER = os.getenv("ORACLE_DB_USER")

    DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD")

    
    DB_DSN = os.getenv("ORACLE_DB_DSN")

    # -------------------------
    # JWT
    # -------------------------

    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "muthoot_fincorp_chatbot_2026")

    ALGORITHM = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    # -------------------------
    # LLM Provider
    # -------------------------

    LLM_PROVIDER = os.getenv(
        "LLM_PROVIDER",
        "openai_compatible"
    ).lower()

    LLM_BASE_URL = os.getenv(
        "LLM_BASE_URL",
        "https://openrouter.ai/api/v1"
    ).rstrip("/")

    LLM_API_KEY = os.getenv("LLM_API_KEY")

    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "qwen/qwen3-8b"
    )

    LLM_TIMEOUT_SECONDS = int(
        os.getenv("LLM_TIMEOUT_SECONDS", "60")
    )

    # Optional local fallback for development only.
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    ).rstrip("/")

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "qwen3:8b"
    )

    # -------------------------
    # Vector Database
    # -------------------------

    VECTOR_DB_PATH = "vector_db"

    FAISS_INDEX = os.path.join(
        VECTOR_DB_PATH,
        "index.faiss"
    )

    DOCUMENT_STORE = os.path.join(
        VECTOR_DB_PATH,
        "documents.pkl"
    )

    FAQ_DOCUMENT = (
        "faq_docs/muthoot_policy.txt"
    )

    # -------------------------
    # Embedding Model
    # -------------------------

    EMBEDDING_MODEL = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )


settings = Settings()
