from browser_manager import switch_tab as browser_switch_tab
import asyncio

def switch_tab(index):
    asyncio.run(browser_switch_tab(index))
    return f"Переключено на вкладку {index}"