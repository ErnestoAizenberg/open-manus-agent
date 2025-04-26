import asyncio
import logging

from browser_manager import BrowserManager
from handle_command import handle_command
from task_registry import register_tasks

logging.basicConfig(level=logging.INFO)
browser_manager = BrowserManager()
tasks = Tasks(browser_manager)                             task_registry = register_tasks(tasks)


async def main():
    try:
        await browser_manager.init_browser(headless=True)
        while True:
            user_input = input("Введите команду (или 'exit' для выхода): ")
            if user_input.lower() == 'exit':
                break
            result = await handle_command(
                task_registry,
                user_input,
            )
            print("\n".join(result))
    finally:
        await browser_manager.close_browser()

if __name__ == "__main__":
    asyncio.run(main())
