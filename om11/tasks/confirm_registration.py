from browser_manager import confirm_registration as browser_confirm_registration
import asyncio

def confirm_registration():
    asyncio.run(browser_confirm_registration())
    return "Регистрация подтверждена"