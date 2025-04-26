from browser_manager import wait_for as browser_wait_for
import asyncio

def wait_for(selector, timeout=5000):
    asyncio.run(browser_wait_for(selector, timeout))
    return f"Дождался элемента {selector}"