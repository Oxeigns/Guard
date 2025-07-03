"""Async SQLite storage utilities for Guard."""

from typing import Optional

import aiosqlite

_connection: Optional[aiosqlite.Connection] = None


async def init_db(path: str) -> None:
    """Initialise the SQLite database."""
    global _connection
    _connection = await aiosqlite.connect(path)
    await _connection.execute("PRAGMA journal_mode=WAL")
    await _connection.execute(
        """CREATE TABLE IF NOT EXISTS warnings(
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            count INTEGER NOT NULL,
            PRIMARY KEY(chat_id, user_id)
        )"""
    )
    await _connection.execute(
        """CREATE TABLE IF NOT EXISTS approved(
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(chat_id, user_id)
        )"""
    )
    await _connection.execute(
        """CREATE TABLE IF NOT EXISTS settings(
            chat_id INTEGER PRIMARY KEY,
            bio_filter INTEGER DEFAULT 1,
            approval_mode INTEGER DEFAULT 0,
            autodelete INTEGER DEFAULT 0
        )"""
    )
    await _connection.commit()


async def close_db() -> None:
    if _connection:
        await _connection.close()


async def get_warnings(chat_id: int, user_id: int) -> int:
    cur = await _connection.execute(
        "SELECT count FROM warnings WHERE chat_id=? AND user_id=?",
        (chat_id, user_id),
    )
    row = await cur.fetchone()
    await cur.close()
    return row[0] if row else 0


async def increment_warning(chat_id: int, user_id: int) -> int:
    count = await get_warnings(chat_id, user_id)
    if count >= 3:
        return count
    await _connection.execute(
        "INSERT INTO warnings(chat_id, user_id, count) VALUES(?,?,1) "
        "ON CONFLICT(chat_id, user_id) DO UPDATE SET count=count+1",
        (chat_id, user_id),
    )
    await _connection.commit()
    return count + 1


async def reset_warning(chat_id: int, user_id: int) -> None:
    await _connection.execute(
        "DELETE FROM warnings WHERE chat_id=? AND user_id=?",
        (chat_id, user_id),
    )
    await _connection.commit()


async def is_approved(chat_id: int, user_id: int) -> bool:
    cur = await _connection.execute(
        "SELECT 1 FROM approved WHERE chat_id=? AND user_id=?",
        (chat_id, user_id),
    )
    row = await cur.fetchone()
    await cur.close()
    return row is not None


async def approve_user(chat_id: int, user_id: int) -> None:
    await _connection.execute(
        "INSERT OR IGNORE INTO approved(chat_id, user_id) VALUES(?, ?)",
        (chat_id, user_id),
    )
    await _connection.commit()


async def unapprove_user(chat_id: int, user_id: int) -> None:
    await _connection.execute(
        "DELETE FROM approved WHERE chat_id=? AND user_id=?",
        (chat_id, user_id),
    )
    await _connection.commit()


async def get_approved(chat_id: int) -> list[int]:
    cur = await _connection.execute(
        "SELECT user_id FROM approved WHERE chat_id=?",
        (chat_id,),
    )
    rows = await cur.fetchall()
    await cur.close()
    return [r[0] for r in rows]


async def get_autodelete(chat_id: int) -> int:
    cur = await _connection.execute(
        "SELECT autodelete FROM settings WHERE chat_id=?",
        (chat_id,),
    )
    row = await cur.fetchone()
    await cur.close()
    return row[0] if row else 0


async def set_autodelete(chat_id: int, seconds: int) -> None:
    await _connection.execute(
        "INSERT INTO settings(chat_id, autodelete) VALUES(?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET autodelete=excluded.autodelete",
        (chat_id, seconds),
    )
    await _connection.commit()


async def get_bio_filter(chat_id: int) -> bool:
    cur = await _connection.execute(
        "SELECT bio_filter FROM settings WHERE chat_id=?",
        (chat_id,),
    )
    row = await cur.fetchone()
    await cur.close()
    return bool(row[0]) if row else True


async def toggle_bio_filter(chat_id: int) -> bool:
    current = await get_bio_filter(chat_id)
    await set_bio_filter(chat_id, not current)
    return not current


async def set_bio_filter(chat_id: int, enabled: bool) -> None:
    await _connection.execute(
        "INSERT INTO settings(chat_id, bio_filter) VALUES(?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET bio_filter=excluded.bio_filter",
        (chat_id, int(enabled)),
    )
    await _connection.commit()


async def get_approval_mode(chat_id: int) -> bool:
    cur = await _connection.execute(
        "SELECT approval_mode FROM settings WHERE chat_id=?",
        (chat_id,),
    )
    row = await cur.fetchone()
    await cur.close()
    return bool(row[0]) if row else False


async def set_approval_mode(chat_id: int, enabled: bool) -> None:
    await _connection.execute(
        "INSERT INTO settings(chat_id, approval_mode) VALUES(?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET approval_mode=excluded.approval_mode",
        (chat_id, int(enabled)),
    )
    await _connection.commit()


async def toggle_approval_mode(chat_id: int) -> bool:
    current = await get_approval_mode(chat_id)
    await set_approval_mode(chat_id, not current)
    return not current
