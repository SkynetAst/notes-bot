import sqlite3

DB_PATH = "notes.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_note(user_id: int, text: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO notes (user_id, text) VALUES (?, ?)",
            (user_id, text),
        )


def get_notes(user_id: int) -> list[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, text, created_at FROM notes WHERE user_id = ? ORDER BY created_at",
            (user_id,),
        )
        return cursor.fetchall()


def delete_note(user_id: int, position: int) -> bool:
    """Delete note by 1-based position in user's list. Returns True if deleted."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            DELETE FROM notes WHERE id = (
                SELECT id FROM notes
                WHERE user_id = ?
                ORDER BY created_at
                LIMIT 1 OFFSET ?
            )
            """,
            (user_id, position - 1),
        )
        return cursor.rowcount > 0
