import mysql.connector
import hashlib

# Hash the password using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="System123@",
        database="phishguard_db"
    )

# Create admin table (if not exists)
def setup_admin_table():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

# Insert a new admin user (Change credentials before running)
def insert_admin_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    
    hashed_pw = hash_password(password)

    try:
        cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()
        print("Admin user added successfully!")
    except mysql.connector.IntegrityError:
        print("Admin user already exists!")

    cursor.close()
    conn.close()

# Run setup
setup_admin_table()
insert_admin_user("admin", "admin123")  
