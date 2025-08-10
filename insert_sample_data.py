import sqlite3

conn = sqlite3.connect("food_wastage.db")
cursor = conn.cursor()

cursor.executemany("""
INSERT INTO providers (Provider_ID, Name, Provider_Type, City, Contact)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, "FreshMart", "Grocery", "New York", "123-456"),
    (2, "GoodEats", "Restaurant", "Los Angeles", "555-789"),
])

cursor.executemany("""
INSERT INTO receivers (Receiver_ID, Name, City, Contact)
VALUES (?, ?, ?, ?)
""", [
    (1, "FoodBankNY", "New York", "987-654"),
    (2, "LA Homeless Shelter", "Los Angeles", "444-321"),
])

cursor.executemany("""
INSERT INTO food_listings (Listing_ID, Provider_ID, Food_Type, Quantity, Provider_Type, City)
VALUES (?, ?, ?, ?, ?, ?)
""", [
    (1, 1, "Bread", 50, "Grocery", "New York"),
    (2, 2, "Pasta", 30, "Restaurant", "Los Angeles"),
])

cursor.executemany("""
INSERT INTO claims (Claim_ID, Receiver_ID, Listing_ID, Status, Meal_Type)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, 1, 1, "Completed", "Dinner"),
    (2, 2, 2, "Pending", "Lunch"),
])

conn.commit()
conn.close()
print("Sample data inserted!")
