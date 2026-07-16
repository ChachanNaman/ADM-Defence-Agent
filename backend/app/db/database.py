import sqlite3
from pathlib import Path
from contextlib import contextmanager

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BACKEND_DIR / "data" / "adm_defender.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _ensure_reviewer_columns(conn: sqlite3.Connection) -> None:
    """PRD v2 change 2 — decision_log predates the reviewer_action columns,
    so CREATE TABLE IF NOT EXISTS won't retrofit them onto an existing db."""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(decision_log)").fetchall()}
    if "reviewer_action" not in columns:
        conn.execute("ALTER TABLE decision_log ADD COLUMN reviewer_action TEXT DEFAULT NULL")
    if "reviewer_action_at" not in columns:
        conn.execute("ALTER TABLE decision_log ADD COLUMN reviewer_action_at TEXT DEFAULT NULL")
    conn.commit()


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.commit()
        _ensure_reviewer_columns(conn)
    finally:
        conn.close()
