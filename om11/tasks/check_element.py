from browser_manager import check_element as browser_check_element
import asyncio

def check_element(selector):
    result = asyncio.run(browser_check_element(selector))
    return f"Элемент {'найден' if result else 'не найден'}: {selector}"