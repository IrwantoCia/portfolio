import sqlite3
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class History:
    resource_id: str
    role: str
    content: str
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[str] = None

    @classmethod
    def from_row(cls, row: tuple) -> "History":
        return cls(
            id=row[0],
            resource_id=row[1],
            role=row[2],
            content=row[3],
            metadata=row[4],
            timestamp=datetime.fromisoformat(row[5]) if row[5] else None,
        )


class SqliteSaver:
    def __init__(self, db_path: str = "memory.sqlite") -> None:
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self.conn.commit()

    def insert(self, items: list[History]) -> None:
        items_tuples = [
            (item.resource_id, item.role, item.content, item.metadata) for item in items
        ]
        self.cursor.executemany(
            "INSERT INTO history (resource_id, role, content, metadata) VALUES (?, ?, ?, ?)",
            items_tuples,
        )
        self.conn.commit()

    def delete(self, resource_id: str) -> None:
        self.cursor.execute("DELETE FROM history WHERE resource_id = ?", (resource_id,))
        self.conn.commit()

    def delete_all(self) -> None:
        self.cursor.execute("DELETE FROM history")
        self.conn.commit()

    def get(self, resource_id: str) -> list[History]:
        self.cursor.execute(
            "SELECT * FROM history WHERE resource_id = ? ORDER BY timestamp",
            (resource_id,),
        )
        return [History.from_row(row) for row in self.cursor.fetchall()]

    def get_all_resource_id(self) -> list[str]:
        self.cursor.execute(
            "SELECT DISTINCT resource_id FROM history ORDER BY timestamp DESC"
        )
        return [row[0] for row in self.cursor.fetchall()]

    def __del__(self) -> None:
        if self.conn:
            self.conn.close()
