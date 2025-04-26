from browser_manager import screenshot as browser_screenshot
import asyncio

def screenshot(filename="screenshot.png"):
    asyncio.run(browser_screenshot(filename))
    return f"Скриншот сохранен: {filename}"