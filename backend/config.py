import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    # -------------------------
    # Oracle Database
    # -------------------------

    DB_USER = os.getenv("DB_USER")

    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DB_DSN = os.getenv("DB_DSN")

    # -------------------------
    # JWT
    # -------------------------

    SECRET_KEY = os.getenv("SECRET_KEY")

    ALGORITHM = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    # -------------------------
    # Gemini
    # -------------------------

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )

    GEMINI_MODEL = "gemini-2.5-flash"

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