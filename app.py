# app.py
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

DB_PATH = "food_wastage.db"

# ---------- Helpers ----------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def run_sql_df(query, params=None):
    with get_conn() as conn:
        if params:
            return pd.read_sql_query(query, conn, params=params)
        return pd.read_sql_query(query, conn)

def exec_sql(query, params=None):
    with get_conn() as conn:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        return cur.lastrowid

def get_distinct_values(table, column):
    try:
        df = run_sql_df(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
        return sorted(df[column].dropna().tolist())
    except Exception:
        return []

def contact_link(contact):
    # if contact looks like email, use mailto
    if isinstance(contact, str) and "@" in contact:
        return f"mailto:{contact}"
    else:
        # phone link
        return f"tel:{contact}"

# ---------- Page config ----------
st.set_page_config(page_title="Local Food Wastage Management", layout="wide")
st.title("🍽 Local Food Wastage Management System")

# ---------- Sidebar navigation ----------
menu = st.sidebar.selectbox("Menu", ["View Data", "Add Food", "Update Quantity", "Delete Food", "Make Claim", "Analysis"])
st.sidebar.markdown("---")
st.sidebar.markdown("**Database:** `food_wastage.db`")

# ---------- View Data ----------
if menu == "View Data":
    st.header("View Data & Filters")
    # filters
    cities = get_distinct_values("food_listings", "City")
    provider_ids = run_sql_df("SELECT Provider_ID, Name FROM providers") if "providers" in run_sql_df(
        "SELECT name FROM sqlite_master WHERE type='table'")["name"].tolist() else pd.DataFrame(columns=["Provider_ID","Name"])
    provider_map = {int(r["Provider_ID"]): r["Name"] for _, r in provider_ids.iterrows()} if not provider_ids.empty else {}
    providers_list = ["All"] + list(provider_map.values())
    food_types = get_distinct_values("food_listings", "Food_Type")

    col1, col2, col3 = st.columns(3)
    with col1:
        city_filter = st.selectbox("City", options=["All"] + cities)
    with col2:
        provider_filter = st.selectbox("Provider (Name)", options=providers_list)
    with col3:
        food_type_filter = st.selectbox("Food Type", options=["All"] + food_types)

    # Build query
    query = "SELECT fl.Listing_ID, fl.Food_Type, fl.Quantity, fl.Provider_Type, fl.City, p.Name AS Provider_Name, p.Contact AS Provider_Contact FROM food_listings fl LEFT JOIN providers p ON fl.Provider_ID = p.Provider_ID WHERE 1=1"
    params = []
    if city_filter != "All":
        query += " AND fl.City = ?"
        params.append(city_filter)
    if provider_filter != "All":
        # provider name -> provider id
        # safe approach: query provider_id by name
        pid_df = run_sql_df("SELECT Provider_ID FROM providers WHERE Name = ?", params=[provider_filter])
        if not pid_df.empty:
            query += " AND fl.Provider_ID = ?"
            params.append(int(pid_df.iloc[0,0]))
        else:
            # no provider match -> no results
            st.info("No provider found with that name.")
            st.stop()
    if food_type_filter != "All":
        query += " AND fl.Food_Type = ?"
        params.append(food_type_filter)

    query += " ORDER BY fl.Listing_ID DESC"
    df_view = run_sql_df(query, params=params if params else None)

    st.subheader("Food Listings (filtered)")
    st.dataframe(df_view)

    st.subheader("Providers")
    df_providers = run_sql_df("SELECT * FROM providers")
    # clickable contact links
    def mk_contact_html(row):
        c = row["Contact"] if pd.notna(row["Contact"]) else ""
        href = contact_link(c)
        return f'<a href="{href}">{c}</a>' if c else ""
    if not df_providers.empty:
        df_providers_display = df_providers.copy()
        df_providers_display["Contact_Link"] = df_providers_display["Contact"].apply(lambda x: contact_link(x) if pd.notna(x) else "")
        st.dataframe(df_providers_display[["Provider_ID","Name","Provider_Type","City","Contact"]])
    else:
        st.write("No providers found.")

    st.subheader("Receivers")
    df_receivers = run_sql_df("SELECT * FROM receivers")
    if not df_receivers.empty:
        st.dataframe(df_receivers)
    else:
        st.write("No receivers found.")

# ---------- Add Food ----------
elif menu == "Add Food":
    st.header("Add New Food Listing")
    with st.form("add_food_form", clear_on_submit=True):
        provider_options = run_sql_df("SELECT Provider_ID, Name FROM providers") if "providers" in run_sql_df(
            "SELECT name FROM sqlite_master WHERE type='table'")["name"].tolist() else pd.DataFrame(columns=["Provider_ID","Name"])
        provider_map = {r["Name"]: r["Provider_ID"] for _, r in provider_options.iterrows()} if not provider_options.empty else {}
        provider_name = st.selectbox("Provider (select existing provider)", options=["Create New"] + list(provider_map.keys()))
        if provider_name == "Create New":
            new_provider_name = st.text_input("New Provider Name")
            new_provider_type = st.text_input("Provider Type (e.g., Restaurant, Grocery)")
            new_provider_city = st.text_input("City")
            new_provider_contact = st.text_input("Contact (phone or email)")
        else:
            new_provider_name = None
            new_provider_type = None
            new_provider_city = None
            new_provider_contact = None

        food_type = st.text_input("Food Type (e.g., Bread, Rice, Salad)")
        quantity = st.number_input("Quantity (units)", min_value=1, value=1)
        provider_type_field = st.text_input("Provider Type (optional, e.g., Grocery, Restaurant)")
        location = st.text_input("Location / City", value=new_provider_city if new_provider_city else "")
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
        submitted = st.form_submit_button("Add Food Listing")
        if submitted:
            conn = get_conn()
            cur = conn.cursor()
            try:
                if provider_name == "Create New":
                    # insert provider
                    cur.execute(
                        "INSERT INTO providers (Name, Provider_Type, City, Contact) VALUES (?, ?, ?, ?)",
                        (new_provider_name, new_provider_type, new_provider_city, new_provider_contact)
                    )
                    provider_id = cur.lastrowid
                else:
                    provider_id = provider_map[provider_name]
                # insert listing
                cur.execute(
                    "INSERT INTO food_listings (Provider_ID, Food_Type, Quantity, Provider_Type, City) VALUES (?, ?, ?, ?, ?)",
                    (provider_id, food_type, int(quantity), provider_type_field if provider_type_field else None, location)
                )
                conn.commit()
                st.success("Food listing added.")
            except Exception as e:
                st.error(f"Error adding listing: {e}")
            finally:
                conn.close()

# ---------- Update Quantity ----------
elif menu == "Update Quantity":
    st.header("Update Food Quantity")
    df_listings = run_sql_df("SELECT fl.Listing_ID, fl.Food_Type, fl.Quantity, p.Name AS Provider_Name FROM food_listings fl LEFT JOIN providers p ON fl.Provider_ID = p.Provider_ID")
    if df_listings.empty:
        st.info("No listings to update.")
    else:
        selected = st.selectbox("Select listing to update", options=df_listings["Listing_ID"].tolist(), format_func=lambda x: f"{x} - {df_listings[df_listings['Listing_ID']==x].iloc[0]['Food_Type']} (qty {df_listings[df_listings['Listing_ID']==x].iloc[0]['Quantity']})")
        new_qty = st.number_input("New Quantity", min_value=0, value=int(df_listings[df_listings["Listing_ID"]==selected]["Quantity"].iloc[0]))
        if st.button("Update"):
            try:
                exec_sql("UPDATE food_listings SET Quantity = ? WHERE Listing_ID = ?", (int(new_qty), int(selected)))
                st.success("Quantity updated.")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Delete Food ----------
elif menu == "Delete Food":
    st.header("Delete Food Listing")
    df_listings = run_sql_df("SELECT Listing_ID, Food_Type, Quantity FROM food_listings")
    if df_listings.empty:
        st.info("No listings to delete.")
    else:
        sel = st.selectbox("Select listing to delete", df_listings["Listing_ID"].tolist(), format_func=lambda x: f"{x} - {df_listings[df_listings['Listing_ID']==x].iloc[0]['Food_Type']}")
        if st.button("Delete"):
            try:
                exec_sql("DELETE FROM food_listings WHERE Listing_ID = ?", (int(sel),))
                st.success("Listing deleted.")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Make Claim ----------
elif menu == "Make Claim":
    st.header("Create a Claim (Receiver claims a Listing)")
    df_receivers = run_sql_df("SELECT Receiver_ID, Name FROM receivers")
    df_listings = run_sql_df("SELECT Listing_ID, Food_Type, Quantity FROM food_listings")
    if df_receivers.empty or df_listings.empty:
        st.info("Need receivers and listings to create claims.")
    else:
        r_sel = st.selectbox("Receiver", options=df_receivers["Receiver_ID"].tolist(), format_func=lambda x: f"{x} - {df_receivers[df_receivers['Receiver_ID']==x].iloc[0]['Name']}")
        l_sel = st.selectbox("Listing", options=df_listings["Listing_ID"].tolist(), format_func=lambda x: f"{x} - {df_listings[df_listings['Listing_ID']==x].iloc[0]['Food_Type']}")
        status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"])
        meal = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
        if st.button("Create Claim"):
            try:
                exec_sql("INSERT INTO claims (Receiver_ID, Listing_ID, Status, Meal_Type) VALUES (?, ?, ?, ?)",
                         (int(r_sel), int(l_sel), status, meal))
                st.success("Claim created.")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- Analysis ----------
elif menu == "Analysis":
    st.header("📊 Analysis & SQL Answers")
    st.markdown("All queries run against `food_wastage.db`. Expand each section to see results.")

    # Query 1: providers & receivers per city
    with st.expander("1. How many food providers and receivers are there in each city?"):
        q1 = """
        SELECT city, 
               SUM(provider_count) AS Provider_Count,
               SUM(receiver_count) AS Receiver_Count
        FROM (
            SELECT City as city, COUNT(Provider_ID) AS provider_count, 0 AS receiver_count FROM providers GROUP BY City
            UNION ALL
            SELECT City as city, 0 AS provider_count, COUNT(Receiver_ID) AS receiver_count FROM receivers GROUP BY City
        )
        GROUP BY city
        ORDER BY Provider_Count DESC;
        """
        st.dataframe(run_sql_df(q1))

    # Query 2: provider type that contributes the most food (by total quantity)
    with st.expander("2. Which type of food provider contributes the most food?"):
        q2 = """
        SELECT f.Provider_Type AS Provider_Type, SUM(f.Quantity) AS Total_Quantity
        FROM food_listings f
        GROUP BY f.Provider_Type
        ORDER BY Total_Quantity DESC;
        """
        st.dataframe(run_sql_df(q2))

    # Query 3: contact info of providers in a specific city (selectable)
    with st.expander("3. Contact information of food providers in a specific city"):
        cities = ["All"] + get_distinct_values("providers", "City")
        sel_city = st.selectbox("Select city for provider contacts", cities, key="contact_city")
        if sel_city == "All":
            st.dataframe(run_sql_df("SELECT Provider_ID, Name, Provider_Type, City, Contact FROM providers"))
        else:
            st.dataframe(run_sql_df("SELECT Provider_ID, Name, Provider_Type, City, Contact FROM providers WHERE City = ?", params=[sel_city]))

    # Query 4: receivers who have claimed the most food
    with st.expander("4. Which receivers have claimed the most food? (by total quantity)"):
        q4 = """
        SELECT r.Name AS Receiver, SUM(fl.Quantity) AS Total_Claimed
        FROM claims c
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN food_listings fl ON c.Listing_ID = fl.Listing_ID
        GROUP BY r.Name
        ORDER BY Total_Claimed DESC;
        """
        st.dataframe(run_sql_df(q4))

    # Query 5: total quantity of food available
    with st.expander("5. What is the total quantity of food available from all providers?"):
        q5 = "SELECT COALESCE(SUM(Quantity),0) AS Total_Available FROM food_listings;"
        st.dataframe(run_sql_df(q5))

    # Query 6: which city has highest number of food listings
    with st.expander("6. Which city has the highest number of food listings?"):
        q6 = """
        SELECT City, COUNT(*) AS Listing_Count
        FROM food_listings
        GROUP BY City
        ORDER BY Listing_Count DESC;
        """
        st.dataframe(run_sql_df(q6))

    # Query 7: most commonly available food types
    with st.expander("7. What are the most commonly available food types?"):
        q7 = """
        SELECT Food_Type, COUNT(*) AS Count
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY Count DESC;
        """
        st.dataframe(run_sql_df(q7))

    # Query 8: claims per food item
    with st.expander("8. How many food claims have been made for each food item?"):
        q8 = """
        SELECT fl.Food_Type, COUNT(c.Claim_ID) AS Claim_Count
        FROM claims c
        JOIN food_listings fl ON c.Listing_ID = fl.Listing_ID
        GROUP BY fl.Food_Type
        ORDER BY Claim_Count DESC;
        """
        st.dataframe(run_sql_df(q8))

    # Query 9: provider with highest number of successful claims
    with st.expander("9. Which provider has had the highest number of successful (Completed) food claims?"):
        q9 = """
        SELECT p.Name AS Provider, COUNT(c.Claim_ID) AS Successful_Claims
        FROM claims c
        JOIN food_listings fl ON c.Listing_ID = fl.Listing_ID
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Name
        ORDER BY Successful_Claims DESC;
        """
        st.dataframe(run_sql_df(q9))

    # Query 10: claim status percentages
    with st.expander("10. Percentage of food claims: Completed vs Pending vs Cancelled"):
        q10 = """
        SELECT Status, ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
        FROM claims
        GROUP BY Status;
        """
        st.dataframe(run_sql_df(q10))

    # Query 11: average quantity claimed per receiver
    with st.expander("11. What is the average quantity of food claimed per receiver?"):
        q11 = """
        SELECT r.Name AS Receiver, ROUND(AVG(fl.Quantity),2) AS Avg_Quantity_Claimed
        FROM claims c
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN food_listings fl ON c.Listing_ID = fl.Listing_ID
        GROUP BY r.Name
        ORDER BY Avg_Quantity_Claimed DESC;
        """
        st.dataframe(run_sql_df(q11))

    # Query 12: which meal type is claimed the most
    with st.expander("12. Which meal type (Breakfast/Lunch/Dinner/Snacks) is claimed the most?"):
        q12 = """
        SELECT Meal_Type, COUNT(*) AS Claim_Count
        FROM claims
        GROUP BY Meal_Type
        ORDER BY Claim_Count DESC;
        """
        st.dataframe(run_sql_df(q12))

    # Query 13: total quantity donated by each provider
    with st.expander("13. What is the total quantity of food donated by each provider?"):
        q13 = """
        SELECT p.Name AS Provider, COALESCE(SUM(fl.Quantity),0) AS Total_Donated
        FROM providers p
        LEFT JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
        GROUP BY p.Name
        ORDER BY Total_Donated DESC;
        """
        st.dataframe(run_sql_df(q13))

    st.markdown("---")
    st.info("Tip: Use the 'View Data' section to filter and inspect individual listings and contacts. Use 'Add Food' / 'Update Quantity' / 'Delete Food' to manage records.")

# ---------- End ----------
