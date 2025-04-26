from browser_manager import solve_captcha as browser_solve_captcha
import asyncio

def solve_captcha():
    asyncio.run(browser_solve_captcha())
    return "Капча решена"