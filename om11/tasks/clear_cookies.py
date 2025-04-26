from browser_manager import clear_cookies as browser_clear_cookies
import asyncio

def clear_cookies():
    asyncio.run(browser_clear_cookies())
    return "Куки очищены"