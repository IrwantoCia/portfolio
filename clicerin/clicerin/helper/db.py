import sqlite3
from typing import Any
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Chat:
    id: Optional[int]
    model: str
    question: Optional[str]
    response: Optional[str]
    token: Optional[int]
    created_at: datetime

    @classmethod
    def from_db_row(cls, row: tuple):
        return cls(
            id=row[0],
            model=row[1],
            question=row[2],
            response=row[3],
            token=row[4],
            created_at=datetime.fromisoformat(row[4]),
        )


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize DatabaseManager with optional db_path.

        Args:
            db_path: Optional path to the database file. If None, creates/uses 'data.db'
            in the current directory.
        """
        self.db_path = str(Path.cwd() / "data.db") if db_path is None else db_path
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        """Establish a connection to SQLite database.

        Returns:
            sqlite3.Connection: Database connection object
        """
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        """Initialize the database with required tables."""
        conn = self.connect()
        c = conn.cursor()

        # Create chat table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                question TEXT,
                response TEXT,
                token INTEGER
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def query(self, sql: str, params: tuple = ()) -> list[Any]:
        """Execute a SQL query and return results.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of query results
        """
        conn = self.connect()
        c = conn.cursor()
        c.execute(sql, params)
        results = c.fetchall()
        conn.close()
        return results

    def insert_chat(self, chat: Chat) -> None:
        """Insert a new chat into the database.

        Args:
            chat: Chat object to insert

        Returns:
            The ID of the newly inserted chat
        """
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """INSERT INTO chats (model, question, response, token)
               VALUES (?, ?, ?, ?)""",
            (chat.model, chat.question, chat.response, chat.token),
        )
        conn.commit()
        conn.close()

    def update_chat(self, chat: Chat) -> None:
        """Update an existing chat in the database.

        Args:
            chat: Chat object to update with current values
        """
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            """UPDATE chats
               SET model = ?, question = ?, response = ?, token = ?
               WHERE id = ?""",
            (chat.model, chat.question, chat.response, chat.token, chat.id),
        )
        conn.commit()
        conn.close()

    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get a chat by its ID.

        Args:
            chat_id: ID of the chat to retrieve

        Returns:
            Recipe object if found, None otherwise
        """
        chat_sql = "SELECT * FROM chats WHERE id = ?"
        chat_rows = self.query(chat_sql, (chat_id,))

        if not chat_rows:
            return None

        return Chat.from_db_row(chat_rows[0])

    def get_all_chats(self) -> list[Chat]:
        """Get all chats.

        Returns:
            List of Chat objects
        """
        chats = []
        chat_sql = "SELECT * FROM chats"
        chat_rows = self.query(chat_sql)

        chats = [
            Chat.from_db_row(
                chat_row,
            )
            for chat_row in chat_rows
        ]

        return chats
