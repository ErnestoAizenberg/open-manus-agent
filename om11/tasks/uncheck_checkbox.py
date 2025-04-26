from browser_manager import uncheck_checkbox as browser_uncheck_checkbox
import asyncio

def uncheck_checkbox(selector):
    asyncio.run(browser_uncheck_checkbox(selector))
    return f"Чекбокс {selector} снят"