import oracledb
from backend.config import settings


def get_db_connection():
    try:
        connection = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dsn=settings.DB_DSN
        )
        return connection
    except Exception as e:
        print(f"Oracle DB Connection Failure: {e}")
        raise
