from browser_manager import click_captcha_checkbox as browser_click_captcha_checkbox
import asyncio

def click_captcha_checkbox():
    asyncio.run(browser_click_captcha_checkbox())
    return "Клик по капча-чекбоксу"