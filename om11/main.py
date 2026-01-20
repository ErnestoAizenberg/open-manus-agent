import asyncio
import logging
import os
from typing import List, Final

from om11.handle_command import handle_command
from om11.task.browser_manager import BrowserManager
from om11.task.task_registry import register_tasks
from om11.task.tasks import Tasks
from om11.user_manager_v1 import CaptchaConfig, CaptchaService, DBManager
from om11.task.execute_task_chain import TaskRegistry

logging.basicConfig(level=logging.INFO)
headless: Final[bool] = os.getenv("HEADLESS", "false").lower() == "true"
CONFIG_DIR: Final[str] = "instance/user_configs"


async def main() -> None:
    db_manager: DBManager = DBManager(config_dir=CONFIG_DIR)
    captcha_service: CaptchaService = CaptchaService(
        db_manager=db_manager,
        config=CaptchaConfig(),
    )
    browser_manager: BrowserManager = BrowserManager()
    tasks: Tasks = Tasks(
        browser_manager=browser_manager,
        captcha_service=captcha_service,
    )
    task_registry: TaskRegistry = register_tasks(tasks)

    try:
        await browser_manager.init_browser(headless=headless)
        while True:
            user_input: str = str(input("Введите команду (или 'exit' для выхода): "))
            if user_input.lower() == "exit":
                break
            result: List[str] = await handle_command(
                user_input,
                task_registry,
            )
            print("\n".join(result))
    finally:
        await browser_manager.close_browser()


if __name__ == "__main__":
    asyncio.run(main())
