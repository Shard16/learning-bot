import asyncio
from backend.services import summarize_document

async def test_summarize():
    s = await summarize_document('hello world')
    assert 'hello' in s
