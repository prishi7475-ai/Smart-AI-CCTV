import tkinter as tk
from tkinter import messagebox
import hashlib
from database import cursor, conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, phone, password):
    try:
        cursor.execute(
            "INSERT INTO users (email, phone, password) VALUES (?, ?, ?)",
            (email, phone, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False

def login_user(email, password):
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    return cursor.fetchone()