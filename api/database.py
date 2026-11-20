"""Database connection and initialization module using SQLite."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import bcrypt
from api.config import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    CITIZEN_EMAIL,
    CITIZEN_PASSWORD,
    DATABASE_PATH,
)


def get_db_connection() -> sqlite3.Connection:
    """Get SQLite database connection with row factory enabled."""
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Hash password string using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def init_db() -> None:
    """Initialize database tables and seed default users."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Citizen Reports Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_name TEXT,
            contact TEXT,
            landmark TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT,
            hazard_type TEXT NOT NULL,
            vehicles TEXT,
            severity TEXT NOT NULL,
            details TEXT,
            lat REAL,
            lon REAL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            reviewed_at TEXT,
            reviewed_by TEXT
        )
        """
    )

    conn.commit()

    # Seed Admin User if not exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (ADMIN_EMAIL,))
    if not cursor.fetchone():
        admin_hash = hash_password(ADMIN_PASSWORD)
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, role, full_name, created_at)
            VALUES (?, ?, 'admin', 'Traffic Police Admin', ?)
            """,
            (ADMIN_EMAIL, admin_hash, datetime.utcnow().isoformat()),
        )
        print(f"✅ Seeded Admin User: {ADMIN_EMAIL}")

    if CITIZEN_EMAIL and CITIZEN_PASSWORD:
        cursor.execute("SELECT id FROM users WHERE email = ?", (CITIZEN_EMAIL,))
        if not cursor.fetchone():
            citizen_hash = hash_password(CITIZEN_PASSWORD)
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, role, full_name, created_at)
                VALUES (?, ?, 'citizen', 'Sonbhadra Commuter', ?)
                """,
                (CITIZEN_EMAIL, citizen_hash, datetime.utcnow().isoformat()),
            )
            print(f"Seeded Citizen User: {CITIZEN_EMAIL}")

    conn.commit()
    conn.close()
