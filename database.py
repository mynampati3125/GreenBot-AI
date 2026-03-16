import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection():
    return sqlite3.connect("users.db", check_same_thread=False)

def create_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?)",
            (username, hashed_pw)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_pw)
    )
    return cursor.fetchone() is not None
