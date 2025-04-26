from browser_manager import get_inner_text as browser_get_inner_text
import asyncio

def get_inner_text(selector):
    text = asyncio.run(browser_get_inner_text(selector))
    return text