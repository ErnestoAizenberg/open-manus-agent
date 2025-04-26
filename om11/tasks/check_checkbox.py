from browser_manager import check_checkbox as browser_check_checkbox
import asyncio

def check_checkbox(selector):
    asyncio.run(browser_check_checkbox(selector))
    return f"Чекбокс {selector} установлен"