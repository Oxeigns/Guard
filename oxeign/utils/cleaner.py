import asyncio

async def auto_delete(client, command_msg, reply_msg=None, delay=10):
    await asyncio.sleep(delay)
    for msg in filter(None, [command_msg, reply_msg]):
        try:
            await msg.delete()
        except Exception:
            pass
