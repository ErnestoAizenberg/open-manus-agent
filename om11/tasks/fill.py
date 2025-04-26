from browser_manager import fill as browser_fill
import asyncio

def fill(selector, text):
    asyncio.run(browser_fill(selector, text))
    return f"Заполнил {selector} текстом: {text}"