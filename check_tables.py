import sqlite3

# Connect to your database
conn = sqlite3.connect("food_wastage.db")
cursor = conn.cursor()

# List of tables to check
tables = ["providers", "receivers", "food_listings", "claims"]

for table in tables:
    print(f"\nTable: {table}")
    cursor.execute(f"PRAGMA table_info({table})")
    for col in cursor.fetchall():
        print(col)

conn.close()
