import sqlite3

DB_PATH = "database/food_wastage.db"

def add_food(food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type))
    conn.commit()
    conn.close()

def update_food_quantity(food_id, new_quantity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE food_listings SET Quantity = ? WHERE Food_ID = ?", (new_quantity, food_id))
    conn.commit()
    conn.close()

def delete_food(food_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_listings WHERE Food_ID = ?", (food_id,))
    conn.commit()
    conn.close()
