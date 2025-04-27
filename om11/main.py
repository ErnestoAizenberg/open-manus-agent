import asyncio
import logging
import os

from browser_manager import BrowserManager
from handle_command import handle_command
from managers.captcha_service import CaptchaConfig, CaptchaService
from managers.config_manager import UserConfigManager
from task_registry import register_tasks
from tasks import Tasks

logging.basicConfig(level=logging.INFO)
headless = os.getenv("HEADLESS", "false").lower() == "true"
CONFIG_DIR = "instance/user_configs"
config_manager = UserConfigManager(config_dir=CONFIG_DIR)
captcha_service = CaptchaService(
    config_manager=config_manager,
    config=CaptchaConfig(),
)
browser_manager = BrowserManager()
tasks = Tasks(
    browser_manager=browser_manager,
    captcha_service=captcha_service,
)
task_registry = register_tasks(tasks)


async def main():
    try:
        await browser_manager.init_browser(headless=headless)
        while True:
            user_input = input("Введите команду (или 'exit' для выхода): ")
            if user_input.lower() == "exit":
                break
            result = await handle_command(
                user_input,
                task_registry,
            )
            print("\n".join(result))
    finally:
        await browser_manager.close_browser()


if __name__ == "__main__":
    asyncio.run(main())
