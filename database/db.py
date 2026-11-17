"""
Database connection and schema initialization for FITGEN AI.
Uses parameterized SQLite queries with robust connection management.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config.settings import settings


def get_db_path() -> Path:
    """Ensure parent directory exists and return database path."""
    db_path = settings.DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


@contextmanager
def get_db_connection():
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables with parameterized DDL."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                fitness_goal TEXT NOT NULL,
                fitness_level TEXT NOT NULL,
                daily_time_minutes INTEGER NOT NULL,
                equipment_list TEXT NOT NULL,
                plan_title TEXT NOT NULL,
                total_workout_days INTEGER NOT NULL,
                plan_json TEXT NOT NULL,
                notes TEXT DEFAULT ''
            );
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plan_id ON workout_history (plan_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON workout_history (created_at DESC);
        """)
