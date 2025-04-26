from browser_manager import go_back as browser_go_back
import asyncio

def go_back():
    asyncio.run(browser_go_back())
    return "Назад по истории"