from browser_manager import load_session as browser_load_session
import asyncio

def load_session(path="session.json"):
    asyncio.run(browser_load_session(path))
    return "Сессия загружена"