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
user=c##arif,
password=1234,
dsn=DB_DSN
)
    return connection

```
    except Exception as e:
        print(f"Oracle DB Connection Failure: {e}")
        raise
```
