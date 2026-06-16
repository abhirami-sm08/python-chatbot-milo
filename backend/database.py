import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("c##arif")
DB_PASSWORD = os.getenv("1234")
DB_DSN = os.getenv("ORACLE_DB_DSN")

def get_db_connection():
    try:
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
        return connection
    except Exception as e:
        print(f"Oracle DB Connection Failure: {e}")
        raise
