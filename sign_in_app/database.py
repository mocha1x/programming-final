import sqlite3
from datetime import datetime

DB_PATH = "users.db"


def init_db():
    """Create the database and users table if they don't exist."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    username    TEXT    NOT NULL UNIQUE,
                    email       TEXT    NOT NULL UNIQUE,
                    password    TEXT    NOT NULL,
                    created_at  TEXT    NOT NULL
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to initialise database: {e}")


def insert_user(username: str, email: str, hashed_password: str) -> None:
    """Insert a new user record into the database."""
    created_at = datetime.now().isoformat(sep=" ", timespec="seconds")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
                (username, email, hashed_password, created_at),
            )
            conn.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Integrity error: {e}")
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def get_user_by_username(username: str) -> dict | None:
    """Return a user row as a dict, or None if not found."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def username_exists(username: str) -> bool:
    """Return True if the username is already taken."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM users WHERE username = ?", (username,)
            )
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def email_exists(email: str) -> bool:
    """Return True if the email is already registered."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM users WHERE email = ?", (email,)
            )
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")
