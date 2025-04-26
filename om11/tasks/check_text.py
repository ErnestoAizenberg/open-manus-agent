from browser_manager import check_text as browser_check_text
import asyncio

def check_text(text):
    found = asyncio.run(browser_check_text(text))
    return f"Текст {'найден' if found else 'не найден'}: {text}"