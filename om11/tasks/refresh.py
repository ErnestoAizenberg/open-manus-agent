from browser_manager import refresh as browser_refresh
import asyncio

def refresh():
    asyncio.run(browser_refresh())
    return "Страница обновлена"