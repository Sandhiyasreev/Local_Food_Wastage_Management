import sqlite3
import pandas as pd

DB_PATH = "food_wastage.db"  # adjust if your DB file name is different

conn = sqlite3.connect(DB_PATH)

def run_query(query):
    return pd.read_sql_query(query, conn)

print("\nChecking tables in database...")
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print("Existing tables:", list(tables['name']))

print("\n" + "="*80)
print("1. Number of food providers and receivers in each city")
print("="*80)
df1 = run_query("""
SELECT p.City AS City,
       COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
       COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
FROM providers p
LEFT JOIN receivers r ON p.City = r.City
GROUP BY p.City;
""")
print(df1 if not df1.empty else "[No data found]")

print("\n" + "="*80)
print("2. Provider type contributing the most food")
print("="*80)
df2 = run_query("""
SELECT f.Provider_Type,
       SUM(f.Quantity) AS Total_Quantity
FROM food_listings f
GROUP BY f.Provider_Type
ORDER BY Total_Quantity DESC
LIMIT 1;
""")
print(df2 if not df2.empty else "[No data found]")

print("\n" + "="*80)
print("3. Contact info of food providers in New York")
print("="*80)
df3 = run_query("""
SELECT p.Name, p.Contact
FROM providers p
WHERE p.City = 'New York';
""")
print(df3 if not df3.empty else "[No data found]")

print("\n" + "="*80)
print("4. Receivers who claimed the most food")
print("="*80)
df4 = run_query("""
SELECT r.Name,
       SUM(f.Quantity) AS Total_Claimed
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Listing_ID = f.Listing_ID
GROUP BY r.Name
ORDER BY Total_Claimed DESC;
""")
print(df4 if not df4.empty else "[No data found]")

print("\n" + "="*80)
print("5. Total quantity of food available")
print("="*80)
df5 = run_query("""
SELECT SUM(Quantity) AS Total_Food_Available
FROM food_listings;
""")
print(df5)

print("\n" + "="*80)
print("6. City with highest number of food listings")
print("="*80)
df6 = run_query("""
SELECT f.City,
       COUNT(*) AS Listing_Count
FROM food_listings f
GROUP BY f.City
ORDER BY Listing_Count DESC
LIMIT 1;
""")
print(df6 if not df6.empty else "[No data found]")

print("\n" + "="*80)
print("7. Most commonly available food types")
print("="*80)
df7 = run_query("""
SELECT Food_Type,
       COUNT(*) AS Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Count DESC;
""")
print(df7 if not df7.empty else "[No data found]")

print("\n" + "="*80)
print("8. Number of claims per food item")
print("="*80)
df8 = run_query("""
SELECT f.Food_Type,
       COUNT(c.Claim_ID) AS Claim_Count
FROM claims c
JOIN food_listings f ON c.Listing_ID = f.Listing_ID
GROUP BY f.Food_Type
ORDER BY Claim_Count DESC;
""")
print(df8 if not df8.empty else "[No data found]")

print("\n" + "="*80)
print("9. Provider with highest number of successful claims")
print("="*80)
df9 = run_query("""
SELECT p.Name,
       COUNT(c.Claim_ID) AS Successful_Claims
FROM claims c
JOIN food_listings f ON c.Listing_ID = f.Listing_ID
JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Successful_Claims DESC
LIMIT 1;
""")
print(df9 if not df9.empty else "[No data found]")

print("\n" + "="*80)
print("10. Percentage of claims by status")
print("="*80)
df10 = run_query("""
SELECT Status,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
FROM claims
GROUP BY Status;
""")
print(df10 if not df10.empty else "[No data found]")

print("\n" + "="*80)
print("11. Average quantity claimed per receiver")
print("="*80)
df11 = run_query("""
SELECT r.Name,
       ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Listing_ID = f.Listing_ID
GROUP BY r.Name;
""")
print(df11 if not df11.empty else "[No data found]")

print("\n" + "="*80)
print("12. Meal type claimed the most")
print("="*80)
df12 = run_query("""
SELECT Meal_Type,
       COUNT(*) AS Claim_Count
FROM claims
GROUP BY Meal_Type
ORDER BY Claim_Count DESC
LIMIT 1;
""")
print(df12 if not df12.empty else "[No data found]")

print("\n" + "="*80)
print("13. Total quantity donated by each provider")
print("="*80)
df13 = run_query("""
SELECT p.Name,
       SUM(f.Quantity) AS Total_Donated
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC;
""")
print(df13 if not df13.empty else "[No data found]")
