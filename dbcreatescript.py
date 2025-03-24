import sqlite3

def create_database(db_name="insurance.db"):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_number TEXT NOT NULL,
                claim_amount REAL NOT NULL,
                claim_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        ''')

        # Insert sample data
        cursor.execute("INSERT INTO claims (policy_number, claim_amount, claim_date, status) VALUES (?, ?, ?, ?)",
                       ("POL123", 500.00, "2025-03-24", "pending"))
        cursor.execute("INSERT INTO claims (policy_number, claim_amount, claim_date, status) VALUES (?, ?, ?, ?)",
                       ("POL456", 1000.00, "2025-03-23", "approved"))

        conn.commit()
        print(f"Database '{db_name}' created successfully with table 'claims' and sample data.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()