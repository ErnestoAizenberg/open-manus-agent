from browser_manager import init_browser, close_browser
from handle_command import handle_command
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    try:
        await init_browser(headless=True)
        while True:
            user_input = input("Введите команду (или 'exit' для выхода): ")
            if user_input.lower() == 'exit':
                break
            result = handle_command(user_input)
            print("\n".join(result))
    finally:
        await close_browser()

if __name__ == "__main__":
    asyncio.run(main())
