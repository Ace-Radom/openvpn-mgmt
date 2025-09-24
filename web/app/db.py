import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

from app import config


def get_conn():
    conn = sqlite3.connect(config.config["app"]["db_path"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """
    )
    conn.commit()
    conn.close()


def user_exists(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None


def add_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        c.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_user_password(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return check_password_hash(row["password_hash"], password)
    return False
