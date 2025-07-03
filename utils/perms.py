"""Permission helpers."""

from pyrogram.types import ChatMember


async def is_user_admin(member: ChatMember) -> bool:
    """Return whether the member has administrative permissions."""
    return member.status in ("administrator", "creator")
