from browser_manager import wait_captcha_frame as browser_wait_captcha_frame
import asyncio

def wait_captcha_frame():
    asyncio.run(browser_wait_captcha_frame())
    return "Капча фрейм загружен"