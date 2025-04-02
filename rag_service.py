import asyncio
from vector_db import search_mods

async def generate_response(query: str):
    related_mods = search_mods(query)
    messages = [
        f"相关文本: '{mod}'" for mod in related_mods
    ]
    for msg in messages:
        await asyncio.sleep(2)
        yield msg