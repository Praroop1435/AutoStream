import aiosqlite
import json
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

DB_PATH = "autostream.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                platform TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        await db.commit()

async def save_messages(user_id: int, session_id: str, messages: List[BaseMessage]):
    """Saves only the newly appended messages to the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        # First, count how many messages are already in DB for this session
        async with db.execute("SELECT COUNT(*) FROM messages WHERE user_id = ? AND session_id = ?", (user_id, session_id)) as cursor:
            count = (await cursor.fetchone())[0]
            
        # Only insert messages that are newer than what we have in DB
        new_messages = messages[count:]
        for msg in new_messages:
            role = "human" if isinstance(msg, HumanMessage) else "ai" if isinstance(msg, AIMessage) else "system"
            await db.execute(
                "INSERT INTO messages (user_id, session_id, role, content) VALUES (?, ?, ?, ?)",
                (user_id, session_id, role, msg.content)
            )
        await db.commit()

async def load_messages(user_id: int, session_id: str) -> List[BaseMessage]:
    """Loads all messages for a specific session."""
    messages = []
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT role, content FROM messages WHERE user_id = ? AND session_id = ? ORDER BY id ASC", (user_id, session_id)) as cursor:
            async for row in cursor:
                role, content = row
                if role == "human":
                    messages.append(HumanMessage(content=content))
                elif role == "ai":
                    messages.append(AIMessage(content=content))
                else:
                    messages.append(SystemMessage(content=content))
    return messages

async def get_user_by_email(email: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE email = ?", (email,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def create_user(email: str, password_hash: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
        await db.commit()
        return cursor.lastrowid

async def save_lead(user_id: int, name: str, email: str, platform: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO leads (user_id, name, email, platform) VALUES (?, ?, ?, ?)",
            (user_id, name, email, platform)
        )
        await db.commit()

async def get_leads(user_id: int) -> List[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM leads WHERE user_id = ? ORDER BY created_at DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
