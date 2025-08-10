import sqlite3
import pandas as pd

DB_PATH = "database/food_wastage.db"

def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Example query functions
def providers_per_city():
    return run_query("SELECT City, COUNT(*) AS Provider_Count FROM providers GROUP BY City")

def top_food_providers():
    return run_query("""
        SELECT Provider_Type, COUNT(*) AS Total_Foods
        FROM food_listings
        GROUP BY Provider_Type
        ORDER BY Total_Foods DESC
    """)
