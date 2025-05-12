import asyncio
import json
import random
import re
from typing import Any, Callable, List, Optional

from playwright.async_api import (
    Browser,
    Page,
    Playwright,  # BrowserType,
    async_playwright,
)


class BrowserManager:
    def __init__(self):
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
        self._playwright: Optional[Playwright] = None

    async def connect_ws(self, ws_url: str, **kwargs: Any) -> None:
        """
        Connect to an existing browser via WebSocket URL.
        """
        if self._playwright is None:
            self._playwright = await async_playwright().start()

        # Determine connection method based on setup
        # For Chromium, you can use connect_over_cdp if CDP endpoint is available
        # Otherwise, fallback to connect
        try:
            self._browser = await self._playwright.chromium.connect_over_cdp(ws_url)
        except Exception:
            self._browser = await self._playwright.chromium.connect(ws_url)
        self._page = await self._browser.new_page()

    async def init_browser(
        self,
        headless: bool = False,
        user_data_dir: Optional[str] = None,
        args: Optional[List[str]] = None,
    ) -> None:
        """Initialize a new browser instance."""
        if self._playwright is None:
            self._playwright = await async_playwright().start()

        browser_args = ["--no-sandbox", "--disable-setuid-sandbox"]
        if args:
            browser_args.extend(args)

        self._browser = await self._playwright.chromium.launch(
            headless=headless,
            args=browser_args,
            ignore_default_args=["--enable-automation"],  # optional
            # userDataDir is not directly supported; use user_data_dir via executable_path or context
        )
        self._page = await self._browser.new_page()
        await self._page.set_viewport_size({"width": 1280, "height": 800})

    async def close_browser(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def open_url(self, url: str, timeout: int = 30000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.goto(url, wait_until="networkidle", timeout=timeout)
            return True
        except Exception as e:
            raise Exception(f"Failed to open URL {url}: {str(e)}")

    async def fill(self, selector: str, text: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            await self._page.fill(selector, text)
            return True
        except Exception as e:
            raise Exception(f"Failed to fill {selector}: {str(e)}")

    async def click(self, selector: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            await self._page.click(selector)
            return True
        except Exception as e:
            raise Exception(f"Failed to click {selector}: {str(e)}")

    async def check_checkbox(self, selector: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            await self._page.evaluate(
                f'document.querySelector("{selector}").checked = true'
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to check checkbox {selector}: {str(e)}")

    async def uncheck_checkbox(self, selector: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            await self._page.evaluate(
                f'document.querySelector("{selector}").checked = false'
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to uncheck checkbox {selector}: {str(e)}")

    async def check_element(self, selector: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False

    async def check_text(self, text: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            content = await self._page.content()
            return text in content
        except Exception as e:
            raise Exception(f"Failed to check text: {str(e)}")

    async def clear_cookies(self) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.context.clear_cookies()
            return True
        except Exception as e:
            raise Exception(f"Failed to clear cookies: {str(e)}")

    async def get_inner_text(self, selector: str, timeout: int = 5000) -> str:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            text = await self._page.inner_text(selector)
            return text
        except Exception as e:
            raise Exception(f"Failed to get text from {selector}: {str(e)}")

    async def save_session(self, path: str = "session.json") -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            cookies = await self._page.context.cookies()
            with open(path, "w") as f:
                json.dump(cookies, f)
            return True
        except Exception as e:
            raise Exception(f"Failed to save session: {str(e)}")

    async def load_session(self, path: str = "session.json") -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            with open(path, "r") as f:
                cookies = json.load(f)
            await self._page.context.add_cookies(cookies)
            return True
        except Exception as e:
            raise Exception(f"Failed to load session: {str(e)}")

    async def click_captcha_checkbox(self, selector: str, timeout: int = 5000) -> bool:
        return await self.click(selector, timeout)

    async def confirm_registration(self, selector: str, timeout: int = 5000) -> bool:
        return await self.click(selector, timeout)

    async def extract_code_from_text(self, selector: str, timeout: int = 5000) -> str:
        return await self.get_inner_text(selector, timeout)

    async def hover(self, selector: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            await self._page.hover(selector)
            return True
        except Exception as e:
            raise Exception(f"Failed to hover over {selector}: {str(e)}")

    async def random_delay(self, min_delay: int = 100, max_delay: int = 1000) -> None:
        delay = random.randint(min_delay, max_delay) / 1000
        await asyncio.sleep(delay)

    async def refresh(self) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.reload(wait_until="networkidle")
            return True
        except Exception as e:
            raise Exception(f"Failed to refresh page: {str(e)}")

    async def screenshot(self, path: str) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.screenshot(path=path)
            return True
        except Exception as e:
            raise Exception(f"Failed to take screenshot: {str(e)}")

    async def scroll_to(self, selector: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            await self._page.eval_on_selector(
                selector, "element => element.scrollIntoView()"
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to scroll to {selector}: {str(e)}")

    async def select_dropdown(
        self, selector: str, value: str, timeout: int = 5000
    ) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            await self._page.select_option(selector, value)
            return True
        except Exception as e:
            raise Exception(f"Failed to select dropdown {selector}: {str(e)}")

    async def set_user_agent(self, user_agent: str) -> None:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        await self._page.set_user_agent(user_agent)

    async def sleep(self, seconds: float) -> None:
        await asyncio.sleep(seconds)

    async def submit_form(self, selector: str) -> bool:
        return await self.click(selector)

    async def switch_tab(self, tab_index: int) -> bool:
        if self._browser is None:
            raise RuntimeError("Browser is not initialized.")
        try:
            pages = await self._browser.contexts[0].pages()
            if 0 <= tab_index < len(pages):
                self._page = pages[tab_index]
                return True
            else:
                raise IndexError(f"Tab index {tab_index} out of range.")
        except Exception as e:
            raise Exception(f"Failed to switch to tab {tab_index}: {str(e)}")

    async def wait_captcha_frame(self, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(
                'iframe[title="captcha"]', timeout=timeout
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to wait for captcha frame: {str(e)}")

    async def wait_email(
        self, filter_func: Callable[[str], bool], timeout: int = 300
    ) -> None:
        # Not implemented, placeholder
        raise NotImplementedError("This method is not implemented yet.")

    async def wait_for(self, selector: str, timeout: int = 5000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            raise Exception(f"Failed to wait for {selector}: {str(e)}")

    async def move_mouse(self, x: int, y: int) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.mouse.move(x, y)
            return True
        except Exception as e:
            raise Exception(f"Failed to move mouse to ({x}, {y}): {str(e)}")

    async def type_slow(self, selector: str, text: str, delay: float = 0.1) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector)
            for char in text:
                await self._page.type(selector, char)
                await asyncio.sleep(delay)
            return True
        except Exception as e:
            raise Exception(f"Failed to type slowly in {selector}: {str(e)}")

    async def press_enter(self) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.keyboard.press("Enter")
            return True
        except Exception as e:
            raise Exception(f"Failed to press Enter: {str(e)}")

    async def get_links_from_selector(self, selector: str) -> List[str]:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector)
            links = await self._page.eval_on_selector_all(
                selector, "elements => elements.map(element => element.href)"
            )
            return [link for link in links if link]
        except Exception as e:
            raise Exception(f"Failed to get links from {selector}: {str(e)}")

    async def click_link_with_text(self, text: str) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.eval_on_selector_all(
                "a",
                f"""(links) => {{
                    const target = links.find(link => link.textContent.includes('{text}'));
                    if (target) target.click();
                }}""",
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to click link with text '{text}': {str(e)}")

    async def extract_emails_from_page(self) -> List[str]:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            content = await self._page.content()
            email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            emails = re.findall(email_regex, content)
            return list(set(emails))
        except Exception as e:
            raise Exception(f"Failed to extract emails: {str(e)}")

    async def download_file(self, url: str) -> bool:
        # For downloading, navigate to the URL
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.goto(url, wait_until="networkidle")
            return True
        except Exception as e:
            raise Exception(f"Failed to download file from {url}: {str(e)}")

    async def check_element_contains_text(self, selector: str, text: str) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.wait_for_selector(selector)
            element_text = await self._page.inner_text(selector)
            return text in element_text
        except Exception as e:
            raise Exception(f"Failed to check text in {selector}: {str(e)}")

    async def go_back(self, timeout: int = 30000) -> bool:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized.")
        try:
            await self._page.go_back(wait_until="networkidle", timeout=timeout)
            return True
        except Exception:
            return False

    @property
    def page(self) -> Optional[Page]:
        return self._page

    @property
    def browser(self) -> Optional[Browser]:
        return self._browser
