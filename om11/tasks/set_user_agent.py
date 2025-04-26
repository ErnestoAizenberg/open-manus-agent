from browser_manager import set_user_agent as browser_set_user_agent
import asyncio

def set_user_agent(user_agent):
    asyncio.run(browser_set_user_agent(user_agent))
    return f"User-Agent установлен: {user_agent}"