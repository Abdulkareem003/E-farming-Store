# database.py
from flask_mysqldb import MySQL

mysql = None  # Global MySQL object

def init_db(app):
    """Initialize MySQL database with Flask app."""
    global mysql
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = ""  # Leave empty if no password
    app.config["MYSQL_DB"] = "e_farming"
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"
    
    mysql = MySQL(app)

def get_user_by_email(email):
    """Fetch user details from the database by email."""
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user

def insert_user(email, hashed_password):
    """Insert a new user into the database."""
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
    mysql.connection.commit()
    cursor.close()

def store_order(email, total_amount):
    """Store order details in the database."""
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO orders (email, total_amount) VALUES (%s, %s)", (email, total_amount))
    mysql.connection.commit()
    cursor.close()
