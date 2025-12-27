"""Async SQLite store for ChatKit-like conversation memory."""

import aiosqlite
import asyncio
from typing import Any, Dict, List, Optional

class SQLiteStore:
    def __init__(self, db_path: str = "chatkit.db"):
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None

    async def init(self):
        """Initialize the database and tables."""
        self.db = await aiosqlite.connect(self.db_path)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                messages TEXT
            )
        """)
        await self.db.commit()

    async def save_thread(self, thread_id: str, messages: List[Dict[str, Any]]):
        """Save or update a conversation thread."""
        import json
        msgs_json = json.dumps(messages)
        await self.db.execute(
            "INSERT INTO threads(id, messages) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET messages = excluded.messages",
            (thread_id, msgs_json)
        )
        await self.db.commit()

    async def load_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """Load a conversation thread by ID."""
        import json
        async with self.db.execute(
            "SELECT messages FROM threads WHERE id = ?", (thread_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
            return []

    async def load_threads(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Load all threads up to a limit."""
        import json
        async with self.db.execute(
            "SELECT id, messages FROM threads LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"id": row[0], "messages": json.loads(row[1])} for row in rows]

    async def close(self):
        """Close the DB connection."""
        if self.db:
            await self.db.close()
