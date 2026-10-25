import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "students.db"


def get_database_path() -> str:
    """Resolve the configured SQLite database path at runtime."""
    return os.getenv("DATABASE_FILE", str(DEFAULT_DB_PATH))


def get_connection():
    """Create a SQLite database connection with row factory enabled."""
    database_file = get_database_path()
    ensure_database_directory(database_file)
    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the students table if it does not already exist."""
    ensure_database_directory()
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email
            ON students(email)
            WHERE email IS NOT NULL
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_students_phone
            ON students(phone)
            WHERE phone IS NOT NULL
            """
        )
        connection.commit()


def ensure_database_directory(database_file: str | Path | None = None):
    """Ensure the parent directory for the database file exists."""
    target = Path(database_file or get_database_path()).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
