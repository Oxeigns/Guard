"""MongoDB storage helpers."""

from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from config import config


class Storage:
    """MongoDB wrapper for chat and user data."""

    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(config.mongo_uri)
        self.db = self.client.telegram_guard
        self.warnings = self.db.warnings
        self.approvals = self.db.approvals
        self.settings = self.db.settings

    async def increment_warning(self, chat_id: int, user_id: int) -> int:
        """Increment and return the warning count for a user."""
        res = await self.warnings.find_one_and_update(
            {"chat_id": chat_id, "user_id": user_id},
            {"$inc": {"count": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return res["count"]

    async def reset_warnings(self, chat_id: int, user_id: int) -> None:
        """Reset warnings for a user."""
        await self.warnings.delete_one({"chat_id": chat_id, "user_id": user_id})

    async def approve_user(self, chat_id: int, user_id: int) -> None:
        """Add a user to the approval list."""
        await self.approvals.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"approved": True}},
            upsert=True,
        )

    async def unapprove_user(self, chat_id: int, user_id: int) -> None:
        """Remove a user from the approval list."""
        await self.approvals.delete_one({"chat_id": chat_id, "user_id": user_id})

    async def is_approved(self, chat_id: int, user_id: int) -> bool:
        """Check if a user is approved."""
        return bool(
            await self.approvals.find_one({"chat_id": chat_id, "user_id": user_id})
        )

    async def get_approved_users(self, chat_id: int) -> List[int]:
        """Return a list of approved user IDs for a chat."""
        cursor = self.approvals.find({"chat_id": chat_id})
        return [doc["user_id"] async for doc in cursor]
    async def get_settings(self, chat_id: int) -> dict:
        """Retrieve group settings."""
        data = await self.settings.find_one({"chat_id": chat_id})
        return data or {"biomode": True, "autodelete": 0}

    async def update_settings(self, chat_id: int, **kwargs) -> None:
        """Update group settings."""
        await self.settings.update_one(
            {"chat_id": chat_id}, {"$set": kwargs}, upsert=True
        )
