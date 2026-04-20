import sqlite3
import hashlib

# ================================
# DATABASE CONNECTION
# ================================
conn = sqlite3.connect("cctv.db", check_same_thread=False)
cursor = conn.cursor()


# ================================
# PASSWORD HASH FUNCTION
# ================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================================
# INITIALIZE DATABASE
# ================================
def init_db():

    # ============================
    # EVENTS TABLE (Existing)
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT,
        description TEXT,
        video_path TEXT,
        image_path TEXT
    )
    """)

    # ============================
    # NUMBER PLATES TABLE (Existing)
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate_number TEXT,
        timestamp TEXT,
        image_path TEXT
    )
    """)

    # ============================
    # USERS TABLE (NEW - LOGIN SYSTEM)
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT
    )
    """)

    # ============================
    # ALERTS TABLE (NEW - THREAT ALERTS)
    # ============================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        emotion TEXT,
        image_path TEXT,
        email_sent_to TEXT
    )
    """)

    conn.commit()


# ================================
# USER FUNCTIONS
# ================================

def register_user(email, phone, password):
    try:
        cursor.execute(
            "INSERT INTO users (email, phone, password) VALUES (?, ?, ?)",
            (email, phone, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(email, password):
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    return cursor.fetchone()


# ================================
# ALERT LOGGING FUNCTION
# ================================

def log_alert(timestamp, emotion, image_path, email):
    cursor.execute(
        "INSERT INTO alerts (timestamp, emotion, image_path, email_sent_to) VALUES (?, ?, ?, ?)",
        (timestamp, emotion, image_path, email)
    )
    conn.commit()


# ================================
# EVENT LOGGING FUNCTION
# ================================

def log_event(timestamp, event_type, description, video_path, image_path):
    cursor.execute(
        "INSERT INTO events (timestamp, event_type, description, video_path, image_path) VALUES (?, ?, ?, ?, ?)",
        (timestamp, event_type, description, video_path, image_path)
    )
    conn.commit()


# ================================
# PLATE LOGGING FUNCTION
# ================================

def log_plate(plate_number, timestamp, image_path):
    cursor.execute(
        "INSERT INTO plates (plate_number, timestamp, image_path) VALUES (?, ?, ?)",
        (plate_number, timestamp, image_path)
    )
    conn.commit()