import os
import oracledb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read values from .env file
DB_USER = os.getenv("ORACLE_DB_USER")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD")
DB_DSN = os.getenv("ORACLE_DB_DSN")

def get_db_connection():
    try:
        connection = oracledb.connect(
<<<<<<<<< Temporary merge branch 1
            user="c##devika",
            password="devika",
            dsn=DB_DSN
        )

        print("Oracle Database Connected Successfully")
        return connection

    except Exception as e:
        print(f"Oracle DB Connection Failure: {e}")
        raise

    
=========
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
        return connection
    except Exception as e:
        print(f"Oracle DB Connection Failure: {e}")
        raise
>>>>>>>>> Temporary merge branch 2
