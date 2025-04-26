from browser_manager import save_session as browser_save_session
import asyncio

def save_session(path="session.json"):
    asyncio.run(browser_save_session(path))
    return "Сессия сохранена"