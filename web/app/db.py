import sqlite3
from hashlib import sha256
from werkzeug.security import generate_password_hash, check_password_hash

from app import config


def get_conn():
    conn = sqlite3.connect(config.config["app"]["db_path"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> bool:
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("BEGIN TRANSACTION;")
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users_not_verified (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL,
                verify_token TEXT UNIQUE NOT NULL
            );
        """
        )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def user_exists(username: str) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        SELECT EXISTS(
            SELECT 1 FROM users WHERE username = ?
            UNION
            SELECT 1 FROM users_not_verified WHERE username = ?
        );
    """,
        (username, username),
    )
    result = c.fetchone()[0]
    conn.close()
    return bool(result)


def verify_token_exists(token: str) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users_not_verified WHERE verify_token = ?", (token,))
    result = c.fetchone()
    return result is not None


def add_user_not_verified(username: str, password: str, email: str) -> str | None:
    password_hash = generate_password_hash(password)
    verify_token = sha256(f"{username}:{password}:{email}".encode("utf-8")).hexdigest()
    token_len = 24
    while token_len <= 64:
        if not verify_token_exists(verify_token[:token_len]):
            verify_token = verify_token[:token_len]
            break
        token_len += 4
    # although it's almost impossible that two 24-digest tokens collide
    # but just for sure

    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users_not_verified (username, password_hash, email, verify_token) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, verify_token),
        )
        conn.commit()
        return verify_token
    except:
        conn.rollback()
        return None
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
