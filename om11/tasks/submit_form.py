from browser_manager import submit_form as browser_submit_form
import asyncio

def submit_form(selector):
    asyncio.run(browser_submit_form(selector))
    return f"Отправил форму {selector}"