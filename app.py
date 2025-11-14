from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import time

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for session handling

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smart_loan'
}


# -------------------- DATABASE CONNECTION HANDLER --------------------
def get_db_connection():
    """Try to connect to MySQL; retry until available."""
    while True:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            if conn.is_connected():
                return conn
        except Error as e:
            print(f"Database connection error: {e}")
            print("Retrying in 3 seconds...")
            time.sleep(3)


# -------------------- AUTO TABLE CREATION --------------------
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create DB if missing (safe to run repeatedly)
    cursor.execute("CREATE DATABASE IF NOT EXISTS smart_loan")
    cursor.execute("USE smart_loan")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        password VARCHAR(100),
        phone VARCHAR(15),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        gender VARCHAR(20),
        married VARCHAR(10),
        dependents INT,
        education VARCHAR(50),
        self_employed VARCHAR(10),
        applicant_income DECIMAL(10,2),
        coapplicant_income DECIMAL(10,2),
        loan_amount DECIMAL(10,2),
        loan_term INT,
        credit_score DECIMAL(6,2),
        property_area VARCHAR(50),
        loan_status VARCHAR(20),
        total_income DECIMAL(12,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# Create DB + tables at startup (will wait for MySQL if not running)
create_tables()


# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return render_template('index.html')


# User register (GET shows form, POST registers)
@app.route('/user-register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (name, email, password, phone)
                VALUES (%s, %s, %s, %s)
            """, (data.get('name'), data.get('email'), data.get('password'), data.get('phone')))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('user_login'))  # after register, go to login
        except mysql.connector.IntegrityError:
            cursor.close()
            conn.close()
            # Email unique constraint violated
            return render_template('UserRegister.html', error="Email already registered!")
    return render_template('UserRegister.html')


# User login (GET shows form, POST authenticates)
@app.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('user_dashboard'))
        else:
            return render_template('UserLogin.html', error="Invalid credentials!")

    return render_template('UserLogin.html')


# User dashboard - shows user info and loan status
@app.route('/user-dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM loan_applications WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (user_id,))
    loan = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('UserDashboard.html', user=user, loan=loan)


# Apply loan (GET shows form, POST saves application)
@app.route('/apply-loan', methods=['GET', 'POST'])
def apply_loan():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO loan_applications 
            (user_id, gender, married, dependents, education, self_employed, applicant_income, coapplicant_income, 
             loan_amount, loan_term, credit_score, property_area, loan_status, total_income)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            data.get('Gender'), data.get('Married'), int(data.get('Dependents') or 0), data.get('Education'),
            data.get('Self_Employed'), float(data.get('ApplicantIncome') or 0), float(data.get('CoapplicantIncome') or 0),
            float(data.get('LoanAmount') or 0), int(data.get('Loan_Amount_Term') or 0), float(data.get('Credit_Score') or 0),
            data.get('Property_Area'), data.get('Loan_Status') or 'Pending', float(data.get('Total_Income') or 0)
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('user_dashboard'))

    # GET -> render application form
    return render_template('application.html')


# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


# -------------------- Static informational pages (must exist in templates/) --------------------
@app.route('/AdminLogin.html')
def admin_login_page():
    return render_template('AdminLogin.html')


@app.route('/application.html')
def application_page():
    # optionally redirect to /apply-loan if you want unified path
    return render_template('application.html')


@app.route('/T&C.html')
def terms_page():
    return render_template('T&C.html')


@app.route('/Recovermethods.html')
def recover_page():
    return render_template('Recovermethods.html')


@app.route('/TypesofLoan.html')
def loan_types_page():
    return render_template('TypesofLoan.html')


@app.route('/completestage.html')
def complete_stage_page():
    return render_template('completestage.html')


@app.route('/LoanFeatures.html')
def features_page():
    return render_template('LoanFeatures.html')


@app.route('/BankFactors.html')
def bank_factors_page():
    return render_template('BankFactors.html')


@app.route('/RBICompliant.html')
def rbi_page():
    return render_template('RBICompliant.html')


# -------------------- RUN --------------------
if __name__ == '__main__':
    app.run(debug=True)
