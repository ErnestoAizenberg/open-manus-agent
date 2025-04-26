from pyppeteer import launch
from pyppeteer.errors import PageError, TimeoutError
import asyncio
import json
import os

_browser = None
_page = None
_event_loop = None

async def init_browser(headless=False, user_data_dir=None, args=None):
    global _browser, _page, _event_loop
    _event_loop = asyncio.get_event_loop()
    
    default_args = ['--no-sandbox', '--disable-setuid-sandbox']
    if args:
        default_args.extend(args)
    
    _browser = await launch(
        headless=headless,
        args=default_args,
        userDataDir=user_data_dir,
        ignoreHTTPSErrors=True
    )
    _page = await _browser.newPage()
    await _page.setViewport({'width': 1280, 'height': 800})

async def close_browser():
    if _browser:
        await _browser.close()

async def open_url(url, timeout=30000):
    try:
        await _page.goto(url, {'waitUntil': 'networkidle2', 'timeout': timeout})
        return True
    except Exception as e:
        raise Exception(f"Failed to open URL {url}: {str(e)}")

async def fill(selector, text, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.type(selector, text)
        return True
    except Exception as e:
        raise Exception(f"Failed to fill {selector}: {str(e)}")

async def click(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.click(selector)
        return True
    except Exception as e:
        raise Exception(f"Failed to click {selector}: {str(e)}")

async def check_checkbox(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.evaluate(f'document.querySelector("{selector}").checked = true')
        return True
    except Exception as e:
        raise Exception(f"Failed to check checkbox {selector}: {str(e)}")

async def check_element(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        return True
    except:
        return False

async def check_text(text, timeout=5000):
    try:
        content = await _page.content()
        return text in content
    except Exception as e:
        raise Exception(f"Failed to check text: {str(e)}")

async def clear_cookies():
    try:
        await _page.deleteCookie()
        return True
    except Exception as e:
        raise Exception(f"Failed to clear cookies: {str(e)}")

async def get_inner_text(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        return await _page.evaluate(f'document.querySelector("{selector}").innerText')
    except Exception as e:
        raise Exception(f"Failed to get text from {selector}: {str(e)}")

async def save_session(path="session.json"):
    try:
        cookies = await _page.cookies()
        with open(path, 'w') as f:
            json.dump(cookies, f)
        return True
    except Exception as e:
        raise Exception(f"Failed to save session: {str(e)}")

async def load_session(path="session.json"):
    try:
        with open(path, 'r') as f:
            cookies = json.load(f)
            await _page.setCookie(*cookies)
        return True
    except Exception as e:
        raise Exception(f"Failed to load session: {str(e)}")



async def click_captcha_checkbox(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.click(selector)
        return True
    except Exception as e:
        raise Exception(f"Failed to click captcha checkbox {selector}: {str(e)}")

async def confirm_registration(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.click(selector)
        return True
    except Exception as e:
        raise Exception(f"Failed to confirm registration {selector}: {str(e)}")

async def extract_code_from_text(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        return await _page.evaluate(f'document.querySelector("{selector}").innerText')
    except Exception as e:
        raise Exception(f"Failed to extract code from {selector}: {str(e)}")

async def hover(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.hover(selector)
        return True
    except Exception as e:
        raise Exception(f"Failed to hover over {selector}: {str(e)}")

async def random_delay(min_delay=100, max_delay=1000):
    import random
    import time
    delay = random.randint(min_delay, max_delay) / 1000  # convert millis to seconds
    await asyncio.sleep(delay)

async def refresh():
    try:
        await _page.reload({'waitUntil': 'networkidle2'})
        return True
    except Exception as e:
        raise Exception(f"Failed to refresh page: {str(e)}")

async def screenshot(path):
    try:
        await _page.screenshot({'path': path})
        return True
    except Exception as e:
        raise Exception(f"Failed to take screenshot: {str(e)}")

async def scroll_to(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        element = await _page.querySelector(selector)
        await _page.evaluate('(element) => element.scrollIntoView()', element)
        return True
    except Exception as e:
        raise Exception(f"Failed to scroll to {selector}: {str(e)}")

async def select_dropdown(selector, value, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.select(selector, value)
        return True
    except Exception as e:
        raise Exception(f"Failed to select dropdown {selector}: {str(e)}")

async def set_user_agent(user_agent):
    await _page.setUserAgent(user_agent)

async def sleep(seconds):
    await asyncio.sleep(seconds)

async def solve_captcha():
    raise NotImplementedError("This method is not implemented yet.")
    pass

async def submit_form(selector):
    try:
        await _page.waitForSelector(selector)
        await _page.click(selector)
        return True
    except Exception as e:
        raise Exception(f"Failed to submit form {selector}: {str(e)}")

async def switch_tab(tab_index):
    try:
        pages = await _browser.pages()
        if len(pages) > tab_index:
            global _page
            _page = pages[tab_index]
            return True
        else:
            raise Exception(f"Tab index {tab_index} is out of range.")
    except Exception as e:
        raise Exception(f"Failed to switch to tab {tab_index}: {str(e)}")

async def uncheck_checkbox(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.evaluate(f'document.querySelector("{selector}").checked = false')
        return True
    except Exception as e:
        raise Exception(f"Failed to uncheck checkbox {selector}: {str(e)}")

async def upload_file(selector, file_path, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        await _page.uploadFile(selector, file_path)
        return True
    except Exception as e:
        raise Exception(f"Failed to upload file to {selector}: {str(e)}")

async def wait_captcha_frame(timeout=5000):
    try:
        await _page.waitForSelector('iframe[title="captcha"]', {'timeout': timeout})
        return True
    except Exception as e:
        raise Exception(f"Failed to wait for captcha frame: {str(e)}")

async def wait_email(filter_func, timeout=300):
    raise NotImplementedError("This method is not implemented yet.")

async def wait_for(selector, timeout=5000):
    try:
        await _page.waitForSelector(selector, {'timeout': timeout})
        return True
    except Exception as e:
        raise Exception(f"Failed to wait for {selector}: {str(e)}")

async def go_back(timeout=30000):
    global _page
    try:
        # Attempt to navigate back to the previous page in the history.
        await _page.goBack({"waitUntil": "networkidle2", "timeout": timeout})
        return True
    except PageError as e:
        print(f"Page error: {e}")
        return False
    except TimeoutError as e:
        print(f"Timeout error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

