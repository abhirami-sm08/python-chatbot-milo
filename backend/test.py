from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT 'Connected' FROM dual")

for row in cursor:
    print(row)

cursor.close()
conn.close()