import os
import oracledb
from dotenv import load_dotenv

# Load environment variables
from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
# Read values from .env file
DB_USER = os.getenv("ORACLE_DB_USER")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD")
DB_DSN = os.getenv("ORACLE_DB_DSN")

def get_db_connection():
    try:
        print(DB_USER)
        print(DB_PASSWORD)
        print(DB_DSN)
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )

        print("Oracle Database Connected Successfully")
        return connection

    except Exception as e:
        print(f"Oracle DB Connection Failure: {e}")
        raise

    
