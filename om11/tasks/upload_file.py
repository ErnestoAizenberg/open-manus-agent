from browser_manager import upload_file as browser_upload_file
import asyncio

def upload_file(selector, filepath):
    asyncio.run(browser_upload_file(selector, filepath))
    return f"Файл {filepath} загружен в {selector}"