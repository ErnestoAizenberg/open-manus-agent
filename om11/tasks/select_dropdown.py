from browser_manager import select_dropdown as browser_select_dropdown
import asyncio

def select_dropdown(selector, value):
    asyncio.run(browser_select_dropdown(selector, value))
    return f"Выбран пункт {value} из {selector}"