import asyncio

async def generate_response(query: str):
    messages = [
        f"查询: '{query} 处理中'",
        "检索相关内容...",
        "生成回答中...",
        "少女祈祷中...",
        f"最终回答: '{query} 的智能回答'"
    ]
    for msg in messages:
        await asyncio.sleep(2)
        yield msg