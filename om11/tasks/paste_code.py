from browser_manager import fill as browser_fill
import asyncio

def paste_code(selector, code):
    asyncio.run(browser_fill(selector, code))
    return f"Вставлен код {code} в {selector}"