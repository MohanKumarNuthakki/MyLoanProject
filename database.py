import sqlite3

def create_db():
    conn = sqlite3.connect('smartloan.db')
    cursor = conn.cursor()

    # Table for storing loan applications
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Loan_ID TEXT,
                        Gender TEXT,
                        Married TEXT,
                        Dependents TEXT,
                        Education TEXT,
                        Self_Employed TEXT,
                        ApplicantIncome REAL,
                        CoapplicantIncome REAL,
                        LoanAmount REAL,
                        Loan_Amount_Term REAL,
                        Credit_History INTEGER,
                        Property_Area TEXT,
                        Loan_Status TEXT,
                        Total_Income REAL
                    )''')

    # Table for admin credentials
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')

    # Insert default admin if not exists
    cursor.execute("SELECT * FROM admin WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', 'admin123'))

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('smartloan.db')
    conn.row_factory = sqlite3.Row
    return conn

# Run this once
if __name__ == "__main__":
    create_db()
    print("Database initialized successfully ✅")
