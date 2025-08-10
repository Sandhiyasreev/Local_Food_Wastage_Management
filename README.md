
# ♻️ Local Food Wastage Management 🍽️🤝

A complete Streamlit + SQLite project designed to connect food providers (restaurants, grocery stores, etc.) with receivers (charities, shelters, etc.) to reduce food wastage.  
The platform enables easy food listing, claims management, CRUD operations, and SQL-powered insights to optimize food distribution.

---

# 🔧 Features

📍 **Filtering** – View food donations based on location, provider, and food type  
📞 **Direct Contact** – Get contact details of providers & receivers instantly  
📝 **CRUD Operations** – Add, update, and delete food listings, providers, and receivers  
📊 **SQL Analysis** – Answers 13 real-world questions on food donations and claims  
📈 **Insights Dashboard** – See trends in contributions, claims, and demand  

---

# 📌 SQL Analysis Includes:
1. Providers & receivers per city  
2. Most contributing provider type  
3. Provider contact info by city  
4. Top receivers by claims  
5. Total quantity of food available  
6. City with most food listings  
7. Most common food types  
8. Claims per food item  
9. Provider with most successful claims  
10. Claims by status (completed, pending, canceled)  
11. Average quantity claimed per receiver  
12. Most claimed meal type  
13. Total food donated per provider  

---

# 🧠 Technologies Used

- **Python** (SQLite, Pandas, Streamlit)
- **SQL** (data queries & analysis)
- **Streamlit** (UI)
- **Matplotlib** (charts & visualizations)

---

# 📁 Project Structure

Local_Food_Wastage_Management/  
├── create_db.py                     # Create and populate database  
├── insert_sample_data.py             # Insert sample records  
├── analysis.py                       # All-in-one Streamlit app with CRUD + analysis  
├── food_wastage.db                   # SQLite database  
├── requirements.txt                  # Python dependencies  
└── README.md                         # Project description  

---

# 🚀 Installation & Running

```bash
# 1️⃣ Clone the repo
git clone git@github.com:YOUR_USERNAME/Local_Food_Wastage_Management.git
cd Local_Food_Wastage_Management

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run the Streamlit app
streamlit run analysis.py
````

---

# 🧪 Example Use Cases

📌 Connect local restaurants to nearby shelters
📌 Analyze which city has the most food wastage
📌 See which food types are most in demand
📌 Contact providers instantly for urgent needs

---

## 🙋‍♀️ Created By

**Sandhiya Sree V**
📧 [sandhiyasreev@gmail.com](mailto:sandhiyasreev@gmail.com)
🔗 [LinkedIn](https://www.linkedin.com/in/sandhiya-sree-v-3a2321298/)
🌐 [GitHub](https://github.com/Sandhiyasreev)

---

# 📄 License

This project is licensed under the MIT License — feel free to use, modify, and share with credit.

⭐ If you found this project helpful, give it a star!
💬 For feedback or collaboration, feel free to reach out.
