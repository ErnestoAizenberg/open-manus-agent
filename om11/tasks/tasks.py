import os
import random
import re
import time
import json
from typing import Any, Dict, List

from om11.agent.task.captcha_manager import CaptchaSolver


class Tasks:
    def __init__(self, browser_manager, captcha_service):
        self.browser = browser_manager
        self.captcha_service = captcha_service

    # Non-browser tasks
    def sleep(self, seconds: float) -> str:
        time.sleep(seconds)
        return f"Пауза {seconds} сек."

    def log_registration_result(self, status: str) -> str:
        print(f"Статус регистрации: {status}")
        return f"Лог сохранен: {status}"

    def extract_code_from_text(self, text: str) -> str:
        match = re.search(r"\b\d{6}\b", text)
        return match.group(0) if match else "Код не найден"

    def wait_email(self, timeout: int = 30) -> str:
        time.sleep(timeout)
        return f"Ожидание письма: {timeout} сек."

    def random_delay(self, min_sec: float = 1, max_sec: float = 5) -> str:
        duration = random.uniform(min_sec, max_sec)
        time.sleep(duration)
        return f"Случайная пауза: {round(duration, 2)} сек."

    # Browser interaction tasks
    async def wait_for(self, selector: str, timeout: int = 5000) -> str:
        await self.browser.wait_for(selector, timeout)
        return f"Дождался элемента {selector}"

    async def wait_captcha_frame(self) -> str:
        await self.browser.wait_captcha_frame()
        return "Капча фрейм загружен"

    async def upload_file(self, selector: str, filepath: str) -> str:
        await self.browser.upload_file(selector, filepath)
        return f"Файл {filepath} загружен в {selector}"

    async def uncheck_checkbox(self, selector: str) -> str:
        await self.browser.uncheck_checkbox(selector)
        return f"Чекбокс {selector} снят"

    async def switch_tab(self, index: int) -> str:
        await self.browser.switch_tab(index)
        return f"Переключено на вкладку {index}"

    async def submit_form(self, selector: str) -> str:
        await self.browser.submit_form(selector)
        return f"Отправил форму {selector}"

    async def set_user_agent(self, user_agent: str) -> str:
        await self.browser.set_user_agent(user_agent)
        return f"User-Agent установлен: {user_agent}"

    async def select_dropdown(self, selector: str, value: str) -> str:
        await self.browser.select_dropdown(selector, value)
        return f"Выбран пункт {value} из {selector}"

    async def scroll_to(self, selector: str) -> str:
        await self.browser.scroll_to(selector)
        return f"Проскроллил до {selector}"

    async def screenshot(self, filename: str = "screenshot.png") -> str:
        await self.browser.screenshot(filename)
        return f"Скриншот сохранен: {filename}"

    async def save_session(self, path: str = "session.json") -> str:
        await self.browser.save_session(path)
        return "Сессия сохранена"

    async def refresh(self) -> str:
        await self.browser.refresh()
        return "Страница обновлена"

    async def paste_code(self, selector: str, code: str) -> str:
        await self.browser.fill(selector, code)
        return f"Вставлен код {code} в {selector}"

    async def open_url(self, url: str) -> str:
        await self.browser.open_url(url)
        return f"Открыл сайт {url}"

    async def load_session(self, path: str = "session.json") -> str:
        await self.browser.load_session(path)
        return "Сессия загружена"

    async def hover(self, selector: str) -> str:
        await self.browser.hover(selector)
        return f"Навел на элемент {selector}"

    async def go_back(self) -> str:
        await self.browser.go_back()
        return "Назад по истории"

    async def get_inner_text(self, selector: str) -> str:
        return await self.browser.get_inner_text(selector)

    async def fill(self, selector: str, text: str) -> str:
        await self.browser.fill(selector, text)
        return f"Заполнил {selector} текстом: {text}"

    async def click(self, selector: str) -> str:
        await self.browser.click(selector)
        return f"Кликнул по элементу {selector}"

    async def clear_cookies(self) -> str:
        await self.browser.clear_cookies()
        return "Куки очищены"

    async def check_text(self, text: str) -> str:
        found = await self.browser.check_text(text)
        return f"Текст {'найден' if found else 'не найден'}: {text}"

    async def check_element(self, selector: str) -> str:
        result = await self.browser.check_element(selector)
        return f"Элемент {'найден' if result else 'не найден'}: {selector}"

    async def check_checkbox(self, selector: str) -> str:
        await self.browser.check_checkbox(selector)
        return f"Чекбокс {selector} установлен"

    async def confirm_registration(self) -> str:
        await self.browser.confirm_registration()
        return "Регистрация подтверждена"

    async def click_captcha_checkbox(self) -> str:
        await self.browser.click_captcha_checkbox()
        return "Клик по капча-чекбоксу"

    async def check_element_contains_text(self, selector: str, text: str) -> str:
        result = await self.browser.check_element_contains_text(selector, text)
        return f"Текст {'найден' if result else 'не найден'} в {selector}"

    async def click_link_with_text(self, text: str) -> str:
        await self.browser.click_link_with_text(text)
        return f"Клик по ссылке с текстом: {text}"

    async def detect_captcha_type(self) -> Any:
        return await self.browser.detect_captcha_type()

    async def download_file(self, url: str) -> str:
        await self.browser.download_file(url)
        return f"Файл скачан с {url}"

    async def extract_emails_from_page(self) -> List[str]:
        return await self.browser.extract_emails_from_page()

    async def get_links_from_selector(self, selector: str) -> List[str]:
        return await self.browser.get_links_from_selector(selector)

    async def move_mouse(self, x: int, y: int) -> str:
        await self.browser.move_mouse(x, y)
        return f"Мышь перемещена в координаты ({x}, {y})"

    async def press_enter(self) -> str:
        await self.browser.press_enter()
        return "Нажал Enter"

    async def type_slow(self, selector: str, text: str, delay: float = 0.1) -> str:
        await self.browser.type_slow(selector, text, delay)
        return f"Медленно ввёл текст '{text}' в {selector}"

    # File and session management tasks
    def read_paths_from_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        filepath = params.get("file")
        count = params.get("count", None)

        if not filepath:
            raise ValueError("Не указан путь к файлу")

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

        print(f"🔧 Настройка Octo-профиля #{profile_index + 1} из папки: {folder_path}")

        if not folder_path or not os.path.exists(folder_path):
            raise FileNotFoundError(f"Папка не найдена: {folder_path}")

        cookies_file = os.path.join(folder_path, "cookies.json")
        if not os.path.isfile(cookies_file):
            raise FileNotFoundError(f"Файл cookies.json не найден в: {folder_path}")

        print(f"✅ Загружены куки: {cookies_file}")
        print(f"🚀 Профиль Octo #{profile_index + 1} успешно настроен!")

        return {"status": "ok", "folder": folder_path, "profile": profile_index + 1}

    async def solve_best_captcha(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_id = params.get("user_id", "default")

        # Check if the user can use captcha service
        if not self.captcha_service.can_use_captcha(user_id):
            raise ValueError("🚫 Превышен лимит капча-решений для пользователя")

        path = "instance/api_keys/api_keys.json"
        with open(path, "r") as f:
            api_keys: Dict[str, str] = json.load(f)

        async with CaptchaSolver(self.browser.page) as solver:
            status = await solver.solve(api_keys=api_keys)
            if status:
                self.captcha_service.increment_user_usage(user_id)
                return {"status": "ok", "result": status}
            else:
                return {"status": "error", "result": None}
