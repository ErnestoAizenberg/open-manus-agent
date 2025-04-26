from browser_manager import scroll_to as browser_scroll_to
import asyncio

def scroll_to(selector):
    asyncio.run(browser_scroll_to(selector))
    return f"Проскроллил до {selector}"