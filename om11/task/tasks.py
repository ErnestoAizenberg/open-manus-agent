import json
import os
import random
import re
import time
from typing import Any, Dict, List

from om11.task.browser_manager import BrowserManager
from om11.task.captcha_manager import CaptchaSolver


class Tasks:
    def __init__(self, browser_manager: BrowserManager, captcha_service: Any):
        self.browser = browser_manager
        self.captcha_service = captcha_service

    # Non-browser tasks
    def sleep(self, seconds: float) -> str:
        time.sleep(seconds)
        return f"Pause for {seconds} seconds."

    def log_registration_result(self, status: str) -> str:
        print(f"Registration status: {status}")
        return f"Log saved: {status}"

    def extract_code_from_text(self, text: str) -> str:
        match = re.search(r"\b\d{6}\b", text)
        return match.group(0) if match else "Code not found"

    def wait_email(self, timeout: int = 30) -> str:
        time.sleep(timeout)
        return f"Waiting for email: {timeout} seconds."

    def random_delay(self, min_sec: float = 1, max_sec: float = 5) -> str:
        duration = random.uniform(min_sec, max_sec)
        time.sleep(duration)
        return f"Random delay: {round(duration, 2)} seconds."

    # Browser interaction tasks
    async def wait_for(self, selector: str, timeout: int = 5000) -> str:
        await self.browser.wait_for(selector, timeout)
        return f"Element {selector} appeared."

    async def wait_captcha_frame(self) -> str:
        await self.browser.wait_captcha_frame()
        return "Captcha frame loaded."

    async def upload_file(self, selector: str, filepath: str) -> str:
        await self.browser.upload_file(selector, filepath)
        return f"File {filepath} uploaded to {selector}."

    async def uncheck_checkbox(self, selector: str) -> str:
        await self.browser.uncheck_checkbox(selector)
        return f"Checkbox {selector} unchecked."

    async def switch_tab(self, index: int) -> str:
        await self.browser.switch_tab(index)
        return f"Switched to tab {index}."

    async def submit_form(self, selector: str) -> str:
        await self.browser.submit_form(selector)
        return f"Form {selector} submitted."

    async def set_user_agent(self, user_agent: str) -> str:
        await self.browser.set_user_agent(user_agent)
        return f"User-Agent set: {user_agent}"

    async def select_dropdown(self, selector: str, value: str) -> str:
        await self.browser.select_dropdown(selector, value)
        return f"Selected {value} from {selector}."

    async def scroll_to(self, selector: str) -> str:
        await self.browser.scroll_to(selector)
        return f"Scrolled to {selector}."

    async def screenshot(self, filename: str = "screenshot.png") -> str:
        await self.browser.screenshot(filename)
        return f"Screenshot saved: {filename}"

    async def save_session(self, path: str = "session.json") -> str:
        await self.browser.save_session(path)
        return "Session saved."

    async def refresh(self) -> str:
        await self.browser.refresh()
        return "Page refreshed."

    async def paste_code(self, selector: str, code: str) -> str:
        await self.browser.fill(selector, code)
        return f"Code {code} pasted into {selector}."

    async def open_url(self, url: str) -> str:
        await self.browser.open_url(url)
        return f"Opened site {url}."

    async def load_session(self, path: str = "session.json") -> str:
        await self.browser.load_session(path)
        return "Session loaded."

    async def hover(self, selector: str) -> str:
        await self.browser.hover(selector)
        return f"Hovered over {selector}."

    async def go_back(self) -> str:
        await self.browser.go_back()
        return "Navigated back."

    async def get_inner_text(self, selector: str) -> str:
        return await self.browser.get_inner_text(selector)

    async def fill(self, selector: str, text: str) -> str:
        await self.browser.fill(selector, text)
        return f"Filled {selector} with text: {text}"

    async def click(self, selector: str) -> str:
        await self.browser.click(selector)
        return f"Clicked element {selector}"

    async def clear_cookies(self) -> str:
        await self.browser.clear_cookies()
        return "Cookies cleared."

    async def check_text(self, text: str) -> str:
        found = await self.browser.check_text(text)
        return f"Text {'found' if found else 'not found'}: {text}"

    async def check_element(self, selector: str) -> str:
        result = await self.browser.check_element(selector)
        return f"Element {'found' if result else 'not found'}: {selector}"

    async def check_checkbox(self, selector: str) -> str:
        await self.browser.check_checkbox(selector)
        return f"Checkbox {selector} checked."

    async def confirm_registration(self, selector: str, timeout: int = 5000) -> str:
        await self.browser.confirm_registration(selector, timeout)
        return "Registration confirmed."

    async def click_captcha_checkbox(self, selector: str) -> str:
        await self.browser.click_captcha_checkbox(selector)
        return "Captcha checkbox clicked."

    async def check_element_contains_text(self, selector: str, text: str) -> str:
        result = await self.browser.check_element_contains_text(selector, text)
        return f"Text {'found' if result else 'not found'} in {selector}."

    async def click_link_with_text(self, text: str) -> str:
        await self.browser.click_link_with_text(text)
        return f"Clicked link with text: {text}"

    async def detect_captcha_type(self) -> Any:
        # self.browser.context.new_page()
        async with CaptchaSolver(self.browser._page) as solver:
            return solver.detect()

    async def download_file(self, url: str) -> str:
        await self.browser.download_file(url)
        return f"File downloaded from {url}"

    async def extract_emails_from_page(self) -> List[str]:
        return await self.browser.extract_emails_from_page()

    async def get_links_from_selector(self, selector: str) -> List[str]:
        return await self.browser.get_links_from_selector(selector)

    async def move_mouse(self, x: int, y: int) -> str:
        await self.browser.move_mouse(x, y)
        return f"Mouse moved to ({x}, {y})"

    async def press_enter(self) -> str:
        await self.browser.press_enter()
        return "Pressed Enter."

    async def type_slow(self, selector: str, text: str, delay: float = 0.1) -> str:
        await self.browser.type_slow(selector, text, delay)
        return f"Slowly typed '{text}' into {selector}."

    # File and session management tasks
    def read_paths_from_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filepath = params.get("file")
        count = params.get("count", None)

        if not filepath:
            raise ValueError("File path not provided.")

        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if count:
            lines = lines[: int(count)]

        return {"status": "ok", "paths": lines}

    async def run_multiple_sessions_from_file(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        filepath = params.get("file")
        count = params.get("count", 1)

        result = self.read_paths_from_file({"file": filepath, "count": count})
        paths = result["paths"]

        results = []
        for idx, path in enumerate(paths):
            session_result = await self.setup_octo_session_from_folder(
                {"folder_path": path, "profile_index": idx}
            )
            results.append(session_result)

        return {"status": "ok", "results": results}

    async def setup_octo_session_from_folder(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        folder_path = params.get("folder_path")
        profile_index = params.get("profile_index", 0)

        print(
            f"🔧 Setting up Octo profile #{profile_index + 1} from folder: {folder_path}"
        )

        if not folder_path or not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        cookies_file = os.path.join(folder_path, "cookies.json")
        if not os.path.isfile(cookies_file):
            raise FileNotFoundError(f"cookies.json not found in: {folder_path}")

        print(f"✅ Loaded cookies: {cookies_file}")
        print(f"🚀 Octo profile #{profile_index + 1} successfully configured!")

        return {"status": "ok", "folder": folder_path, "profile": profile_index + 1}

    async def solve_best_captcha(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "default")

        # Check if user can use captcha service
        if not self.captcha_service.can_use_captcha(user_id):
            raise ValueError("🚫 User has exceeded captcha limit.")

        api_keys_path = "instance/api_keys/api_keys.json"
        with open(api_keys_path, "r") as f:
            api_keys: Dict[str, str] = json.load(f)

        async with CaptchaSolver(self.browser._page) as solver:
            status = await solver.solve(api_keys=api_keys)
            if status:
                self.captcha_service.increment_user_usage(user_id)
                return {"status": "ok", "result": status}
            else:
                return {"status": "error", "result": None}
