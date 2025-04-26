from browser_manager import open_url as browser_open_url
import asyncio

def open_url(url):
    asyncio.run(browser_open_url(url))
    return f"Открыл сайт {url}"