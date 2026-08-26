import sqlite3
from datetime import datetime


class FeedbackService:
    def __init__(self, db_path: str = "feedback.db"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                message_id TEXT,
                rating TEXT,
                comment TEXT,
                created_at TEXT
            )"""
        )
        self._conn.commit()

    def add(self, conversation_id: str, message_id: str,
            rating: str, comment: str = "") -> None:
        self._conn.execute(
            "INSERT INTO feedback (conversation_id, message_id, rating, comment, created_at)"
            " VALUES (?,?,?,?,?)",
            (conversation_id, message_id, rating, comment, datetime.now().isoformat()),
        )
        self._conn.commit()

    def list(self, limit: int = 100) -> list[dict]:
        rows = self._conn.execute(
            "SELECT id, conversation_id, message_id, rating, comment, created_at"
            " FROM feedback ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            {"id": r[0], "conversation_id": r[1], "message_id": r[2],
             "rating": r[3], "comment": r[4], "created_at": r[5]}
            for r in rows
        ]
