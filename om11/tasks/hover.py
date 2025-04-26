from browser_manager import hover as browser_hover
import asyncio

def hover(selector):
    asyncio.run(browser_hover(selector))
    return f"Навел на элемент {selector}"