# tasks.py
import time
import random
import re
import os
import asyncio
from typing import Any, Dict, Optional
from browser_manager import BrowserManager

# Initialize browser manager (should be initialized once at application start)
_browser_manager = None

async def init_browser_manager(headless=False, user_data_dir=None, args=None):
    global _browser_manager
    _browser_manager = BrowserManager()
    await _browser_manager.init_browser(headless=headless, user_data_dir=user_data_dir, args=args)

async def close_browser_manager():
    global _browser_manager
    if _browser_manager:
        await _browser_manager.close_browser()
        _browser_manager = None

# Helper function for browser operations
async def _run_browser_task(coro_func, *args, **kwargs):
    if _browser_manager is None:
        raise RuntimeError("Browser manager not initialized")
    return await coro_func(*args, **kwargs)

# Task implementations
def sleep(seconds):
    time.sleep(seconds)
    return f"Пауза {seconds} сек."

def log_registration_result(status):
    print(f"Статус регистрации: {status}")
    return f"Лог сохранен: {status}"

def extract_code_from_text(text):
    match = re.search(r"\b\d{6}\b", text)
    return match.group(0) if match else "Код не найден"

def wait_email(timeout=30):
    time.sleep(timeout)
    return f"Ожидание письма: {timeout} сек."

async def wait_for(selector, timeout=5000):
    await _run_browser_task(_browser_manager.wait_for, selector, timeout)
    return f"Дождался элемента {selector}"

async def wait_captcha_frame():
    await _run_browser_task(_browser_manager.wait_captcha_frame)
    return "Капча фрейм загружен"

async def upload_file(selector, filepath):
    await _run_browser_task(_browser_manager.upload_file, selector, filepath)
    return f"Файл {filepath} загружен в {selector}"

async def uncheck_checkbox(selector):
    await _run_browser_task(_browser_manager.uncheck_checkbox, selector)
    return f"Чекбокс {selector} снят"

async def switch_tab(index):
    await _run_browser_task(_browser_manager.switch_tab, index)
    return f"Переключено на вкладку {index}"

async def submit_form(selector):
    await _run_browser_task(_browser_manager.submit_form, selector)
    return f"Отправил форму {selector}"

async def set_user_agent(user_agent):
    await _run_browser_task(_browser_manager.set_user_agent, user_agent)
    return f"User-Agent установлен: {user_agent}"

async def select_dropdown(selector, value):
    await _run_browser_task(_browser_manager.select_dropdown, selector, value)
    return f"Выбран пункт {value} из {selector}"

async def scroll_to(selector):
    await _run_browser_task(_browser_manager.scroll_to, selector)
    return f"Проскроллил до {selector}"

async def screenshot(filename="screenshot.png"):
    await _run_browser_task(_browser_manager.screenshot, filename)
    return f"Скриншот сохранен: {filename}"

async def save_session(path="session.json"):
    await _run_browser_task(_browser_manager.save_session, path)
    return "Сессия сохранена"

async def refresh():
    await _run_browser_task(_browser_manager.refresh)
    return "Страница обновлена"

def random_delay(min_sec=1, max_sec=5):
    duration = random.uniform(min_sec, max_sec)
    time.sleep(duration)
    return f"Случайная пауза: {round(duration, 2)} сек."

async def paste_code(selector, code):
    await _run_browser_task(_browser_manager.fill, selector, code)
    return f"Вставлен код {code} в {selector}"

async def open_url(url):
    await _run_browser_task(_browser_manager.open_url, url)
    return f"Открыл сайт {url}"

async def load_session(path="session.json"):
    await _run_browser_task(_browser_manager.load_session, path)
    return "Сессия загружена"

async def hover(selector):
    await _run_browser_task(_browser_manager.hover, selector)
    return f"Навел на элемент {selector}"

async def go_back():
    await _run_browser_task(_browser_manager.go_back)
    return "Назад по истории"

async def get_inner_text(selector):
    text = await _run_browser_task(_browser_manager.get_inner_text, selector)
    return text

async def fill(selector, text):
    await _run_browser_task(_browser_manager.fill, selector, text)
    return f"Заполнил {selector} текстом: {text}"

async def click(selector):
    await _run_browser_task(_browser_manager.click, selector)
    return f"Кликнул по элементу {selector}"

async def clear_cookies():
    await _run_browser_task(_browser_manager.clear_cookies)
    return "Куки очищены"

async def check_text(text):
    found = await _run_browser_task(_browser_manager.check_text, text)
    return f"Текст {'найден' if found else 'не найден'}: {text}"

async def check_element(selector):
    result = await _run_browser_task(_browser_manager.check_element, selector)
    return f"Элемент {'найден' if result else 'не найден'}: {selector}"

async def check_checkbox(selector):
    await _run_browser_task(_browser_manager.check_checkbox, selector)
    return f"Чекбокс {selector} установлен"

async def confirm_registration():
    await _run_browser_task(_browser_manager.confirm_registration)
    return "Регистрация подтверждена"

async def click_captcha_checkbox():
    await _run_browser_task(_browser_manager.click_captcha_checkbox)
    return "Клик по капча-чекбоксу"

async def check_element_contains_text(selector, text):
    result = await _run_browser_task(_browser_manager.check_element_contains_text, selector, text)
    return f"Текст {'найден' if result else 'не найден'} в {selector}"

async def click_link_with_text(text):
    await _run_browser_task(_browser_manager.click_link_with_text, text)
    return f"Клик по ссылке с текстом: {text}"

async def detect_captcha_type():
    return await _run_browser_task(_browser_manager.detect_captcha_type)

async def download_file(url):
    await _run_browser_task(_browser_manager.download_file, url)
    return f"Файл скачан с {url}"

async def extract_emails_from_page():
    emails = await _run_browser_task(_browser_manager.extract_emails_from_page)
    return emails

async def get_links_from_selector(selector):
    links = await _run_browser_task(_browser_manager.get_links_from_selector, selector)
    return links

async def move_mouse(x, y):
    await _run_browser_task(_browser_manager.move_mouse, x, y)
    return f"Мышь перемещена в координаты ({x}, {y})"

async def press_enter():
    await _run_browser_task(_browser_manager.press_enter)
    return "Нажал Enter"

def read_paths_from_file(params):
    filepath = params.get("file")
    count = params.get("count", None)

    if not filepath:
        raise ValueError("Не указан путь к файлу")

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if count:
        lines = lines[: int(count)]

    return {"status": "ok", "paths": lines}

async def run_multiple_sessions_from_file(params):
    filepath = params.get("file")
    count = params.get("count", 1)

    result = read_paths_from_file({"file": filepath, "count": count})
    paths = result["paths"]

    results = []
    for idx, path in enumerate(paths):
        session_result = await setup_octo_session_from_folder(
            {"folder_path": path, "profile_index": idx}
        )
        results.append(session_result)

    return {"status": "ok", "results": results}

async def setup_octo_session_from_folder(params):
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

async def solve_best_captcha(params: Dict[str, Any]) -> Dict[str, Any]:
    user_id = params.get("user_id", "default")

    if not can_use_captcha(user_id):
        raise Exception("🚫 Превышен лимит капча-решений для пользователя")

    api_keys = load_api_keys()
    captcha_type = "capmonster"

    result = await go(captcha_type, api_keys)

    if result:
        increment_user_usage(user_id)

    return {"status": "ok", "result": result}

async def go(captcha_type: Optional[str], api_keys: Dict[str, str]) -> Optional[bool]:
    if captcha_type is None:
        print("Капча не распознана.")
        return False

    captcha_solvers = {
        "2captcha": _browser_manager.solve_captcha_2captcha,
        "capmonster": _browser_manager.solve_captcha_capmonster,
        "anticaptcha": _browser_manager.solve_captcha_anticaptcha,
        "rucaptcha": _browser_manager.solve_captcha_rucaptcha,
    }

    solve_func = captcha_solvers.get(captcha_type)

    if solve_func is None:
        print(f"Неизвестный тип капчи: {captcha_type}.")
        return False

    api_key = api_keys.get(captcha_type)
    if api_key:
        return await solve_func(api_key)
    return False

async def solve_captcha_2captcha(api_key):
    await _run_browser_task(_browser_manager.solve_captcha_2captcha, api_key)
    return "Капча решена через 2Captcha"

async def solve_captcha_anticaptcha(api_key):
    await _run_browser_task(_browser_manager.solve_captcha_anticaptcha, api_key)
    return "Капча решена через Anti-Captcha"

async def solve_captcha_capmonster(api_key):
    await _run_browser_task(_browser_manager.solve_captcha_capmonster, api_key)
    return "Капча решена через CapMonster"

async def solve_captcha_rucaptcha(api_key):
    await _run_browser_task(_browser_manager.solve_captcha_rucaptcha, api_key)
    return "Капча решена через RuCaptcha"

async def type_slow(selector, text, delay=0.1):
    await _run_browser_task(_browser_manager.type_slow, selector, text, delay)
    return f"Медленно ввёл текст '{text}' в {selector}"
