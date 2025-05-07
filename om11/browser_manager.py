import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from pyppeteer import launch
from pyppeteer.errors import PageError, TimeoutError

from managers.captcha_manager import CaptchaSolver


class BrowserManager:
    def __init__(self):
        self._browser = None
        self._page = None
        self._event_loop = None
        # self._captcha_solver = CaptchaSolver()
        # There are two ways of using CaptchaSolver im BrowserManager:
        # 1) make captcha_solver atribute of browser to set pahe when it needed
        # 2) Usage like this: async with CaptchaSolver(self._page) as solver: solver.solve()

    async def init_browser(
        self,
        headless: bool = False,
        user_data_dir: Optional[str] = None,
        args: Optional[List[str]] = None,
    ) -> None:
        """Initialize the browser instance."""
        self._event_loop = asyncio.get_event_loop()

        default_args = ["--no-sandbox", "--disable-setuid-sandbox"]
        if args:
            default_args.extend(args)

        self._browser = await launch(
            headless=headless,
            args=default_args,
            userDataDir=user_data_dir,
            ignoreHTTPSErrors=True,
        )
        self._page = await self._browser.newPage()
        await self._page.setViewport({"width": 1280, "height": 800})
        # await self._captcha_solver.set_page(self._page)
        # old realisation, but may have a sense

    async def close_browser(self) -> None:
        """Close the browser instance."""
        if self._browser:
            await self._browser.close()

    async def open_url(self, url: str, timeout: int = 30000) -> bool:
        """Navigate to the specified URL."""
        try:
            await self._page.goto(
                url, {"waitUntil": "networkidle2", "timeout": timeout}
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to open URL {url}: {str(e)}")

    async def fill(self, selector: str, text: str, timeout: int = 5000) -> bool:
        """Fill a form field with the specified text."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.type(selector, text)
            return True
        except Exception as e:
            raise Exception(f"Failed to fill {selector}: {str(e)}")

    async def click(self, selector: str, timeout: int = 5000) -> bool:
        """Click on the specified element."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.click(selector)
            return True
        except Exception as e:
            raise Exception(f"Failed to click {selector}: {str(e)}")

    async def check_checkbox(self, selector: str, timeout: int = 5000) -> bool:
        """Check a checkbox element."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.evaluate(
                f'document.querySelector("{selector}").checked = true'
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to check checkbox {selector}: {str(e)}")

    async def check_element(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element exists on the page."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            return True
        except:
            return False

    async def check_text(self, text: str, timeout: int = 5000) -> bool:
        """Check if text exists on the page."""
        try:
            content = await self._page.content()
            return text in content
        except Exception as e:
            raise Exception(f"Failed to check text: {str(e)}")

    async def clear_cookies(self) -> bool:
        """Clear all cookies."""
        try:
            await self._page.deleteCookie()
            return True
        except Exception as e:
            raise Exception(f"Failed to clear cookies: {str(e)}")

    async def get_inner_text(self, selector: str, timeout: int = 5000) -> str:
        """Get the inner text of an element."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            return await self._page.evaluate(
                f'document.querySelector("{selector}").innerText'
            )
        except Exception as e:
            raise Exception(f"Failed to get text from {selector}: {str(e)}")

    async def save_session(self, path: str = "session.json") -> bool:
        """Save the current session cookies to a file."""
        try:
            cookies = await self._page.cookies()
            with open(path, "w") as f:
                json.dump(cookies, f)
            return True
        except Exception as e:
            raise Exception(f"Failed to save session: {str(e)}")

    async def load_session(self, path: str = "session.json") -> bool:
        """Load a session from cookies file."""
        try:
            with open(path, "r") as f:
                cookies = json.load(f)
                await self._page.setCookie(*cookies)
            return True
        except Exception as e:
            raise Exception(f"Failed to load session: {str(e)}")

    async def click_captcha_checkbox(self, selector: str, timeout: int = 5000) -> bool:
        """Click on a captcha checkbox."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.click(selector)
            return True
        except Exception as e:
            raise Exception(f"Failed to click captcha checkbox {selector}: {str(e)}")

    async def confirm_registration(self, selector: str, timeout: int = 5000) -> bool:
        """Confirm registration by clicking a button."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.click(selector)
            return True
        except Exception as e:
            raise Exception(f"Failed to confirm registration {selector}: {str(e)}")

    async def extract_code_from_text(self, selector: str, timeout: int = 5000) -> str:
        """Extract code/text from an element."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            return await self._page.evaluate(
                f'document.querySelector("{selector}").innerText'
            )
        except Exception as e:
            raise Exception(f"Failed to extract code from {selector}: {str(e)}")

    async def hover(self, selector: str, timeout: int = 5000) -> bool:
        """Hover over an element."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.hover(selector)
            return True
        except Exception as e:
            raise Exception(f"Failed to hover over {selector}: {str(e)}")

    async def random_delay(self, min_delay: int = 100, max_delay: int = 1000) -> None:
        """Add a random delay between actions."""
        import random

        delay = random.randint(min_delay, max_delay) / 1000  # convert millis to seconds
        await asyncio.sleep(delay)

    async def refresh(self) -> bool:
        """Refresh the current page."""
        try:
            await self._page.reload({"waitUntil": "networkidle2"})
            return True
        except Exception as e:
            raise Exception(f"Failed to refresh page: {str(e)}")

    async def screenshot(self, path: str) -> bool:
        """Take a screenshot of the current page."""
        try:
            await self._page.screenshot({"path": path})
            return True
        except Exception as e:
            raise Exception(f"Failed to take screenshot: {str(e)}")

    async def scroll_to(self, selector: str, timeout: int = 5000) -> bool:
        """Scroll to a specific element."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            element = await self._page.querySelector(selector)
            await self._page.evaluate("(element) => element.scrollIntoView()", element)
            return True
        except Exception as e:
            raise Exception(f"Failed to scroll to {selector}: {str(e)}")

    async def select_dropdown(
        self, selector: str, value: str, timeout: int = 5000
    ) -> bool:
        """Select an option from a dropdown."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.select(selector, value)
            return True
        except Exception as e:
            raise Exception(f"Failed to select dropdown {selector}: {str(e)}")

    async def set_user_agent(self, user_agent: str) -> None:
        """Set the user agent for the browser."""
        await self._page.setUserAgent(user_agent)

    async def sleep(self, seconds: float) -> None:
        """Sleep for the specified number of seconds."""
        await asyncio.sleep(seconds)

    async def submit_form(self, selector: str) -> bool:
        """Submit a form."""
        try:
            await self._page.waitForSelector(selector)
            await self._page.click(selector)
            return True
        except Exception as e:
            raise Exception(f"Failed to submit form {selector}: {str(e)}")

    async def switch_tab(self, tab_index: int) -> bool:
        """Switch to a different browser tab."""
        try:
            pages = await self._browser.pages()
            if len(pages) > tab_index:
                self._page = pages[tab_index]
                # await self._captcha_solver.set_page(self._page)
                # old realisation but may have a sanse
                return True
            else:
                raise Exception(f"Tab index {tab_index} is out of range.")
        except Exception as e:
            raise Exception(f"Failed to switch to tab {tab_index}: {str(e)}")

    async def uncheck_checkbox(self, selector: str, timeout: int = 5000) -> bool:
        """Uncheck a checkbox."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.evaluate(
                f'document.querySelector("{selector}").checked = false'
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to uncheck checkbox {selector}: {str(e)}")

    async def upload_file(
        self, selector: str, file_path: str, timeout: int = 5000
    ) -> bool:
        """Upload a file to a file input."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            await self._page.uploadFile(selector, file_path)
            return True
        except Exception as e:
            raise Exception(f"Failed to upload file to {selector}: {str(e)}")

    async def wait_captcha_frame(self, timeout: int = 5000) -> bool:
        """Wait for a captcha frame to load."""
        try:
            await self._page.waitForSelector(
                'iframe[title="captcha"]', {"timeout": timeout}
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to wait for captcha frame: {str(e)}")

    async def wait_email(self, filter_func, timeout: int = 300) -> None:
        """Wait for an email (not implemented)."""
        raise NotImplementedError("This method is not implemented yet.")

    async def wait_for(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for an element to appear."""
        try:
            await self._page.waitForSelector(selector, {"timeout": timeout})
            return True
        except Exception as e:
            raise Exception(f"Failed to wait for {selector}: {str(e)}")

    async def move_mouse(self, x: int, y: int) -> bool:
        """Move the mouse to specific coordinates."""
        try:
            await self._page.mouse.move(x, y)
            return True
        except Exception as e:
            raise Exception(f"Failed to move mouse to ({x}, {y}): {str(e)}")

    async def type_slow(self, selector: str, text: str, delay: float = 0.1) -> bool:
        """Type text slowly to simulate human typing."""
        try:
            await self._page.waitForSelector(selector)
            for char in text:
                await self._page.type(selector, char)
                await asyncio.sleep(delay)
            return True
        except Exception as e:
            raise Exception(f"Failed to type slowly in {selector}: {str(e)}")

    async def press_enter(self) -> bool:
        """Press the Enter key."""
        try:
            await self._page.keyboard.press("Enter")
            return True
        except Exception as e:
            raise Exception(f"Failed to press Enter: {str(e)}")

    async def get_links_from_selector(self, selector: str) -> List[str]:
        """Get all links matching the selector."""
        try:
            await self._page.waitForSelector(selector)
            links = await self._page.evaluate(
                f"""
                Array.from(document.querySelectorAll('{selector}'))
                    .map(element => element.href)
            """
            )
            return [link for link in links if link]  # Filter out None/empty links
        except Exception as e:
            raise Exception(f"Failed to get links from {selector}: {str(e)}")

    async def click_link_with_text(self, text: str) -> bool:
        """Click a link containing specific text."""
        try:
            await self._page.evaluate(
                f"""
                const links = Array.from(document.querySelectorAll('a'));
                const target = links.find(link => link.textContent.includes('{text}'));
                if (target) target.click();
            """
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to click link with text '{text}': {str(e)}")

    async def extract_emails_from_page(self) -> List[str]:
        """Extract all email addresses from the page."""
        try:
            content = await self._page.content()
            import re

            email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            emails = re.findall(email_regex, content)
            return list(set(emails))  # Remove duplicates
        except Exception as e:
            raise Exception(f"Failed to extract emails: {str(e)}")

    async def download_file(self, url: str) -> bool:
        """Download a file from the specified URL."""
        try:
            await self._page.goto(url, {"waitUntil": "networkidle2"})
            return True
        except Exception as e:
            raise Exception(f"Failed to download file from {url}: {str(e)}")

    async def check_element_contains_text(self, selector: str, text: str) -> bool:
        """Check if an element contains specific text."""
        try:
            await self._page.waitForSelector(selector)
            element_text = await self._page.evaluate(
                f"""
                document.querySelector('{selector}').textContent
            """
            )
            return text in element_text
        except Exception as e:
            raise Exception(f"Failed to check text in {selector}: {str(e)}")

    async def go_back(self, timeout: int = 30000) -> bool:
        """Navigate back in browser history."""
        try:
            await self._page.goBack({"waitUntil": "networkidle2", "timeout": timeout})
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

    @property
    def page(self):
        """Get the current page object."""
        return self._page

    @property
    def browser(self):
        """Get the browser object."""
        return self._browser
