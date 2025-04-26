import asyncio
from pyppeteer import connect
from pyppeteer.errors import NetworkError
from command_executor import CommandExecutor

async def test_manus_agent_on_browserstack():
    # Конфигурация BrowserStack
    BROWSERSTACK_USER = "sereernest@gmail.com"
    BROWSERSTACK_KEY = "PoF4jrAZXDDUsX2WysDC"
    BROWSERSTACK_CDP_URL = f"wss://cdp.browserstack.com/puppeteer?user={BROWSERSTACK_USER}&key={BROWSERSTACK_KEY}"

    try:
        print("🔄 Подключаемся к BrowserStack...")
        browser = await connect(
            browserWSEndpoint=BROWSERSTACK_CDP_URL,
            # Дополнительные параметры для стабильности
            ignoreHTTPSErrors=True,
            slowMo=100,  # Замедление для отладки
        )
        page = await browser.newPage()
        print("✅ Успешное подключение")

        executor = CommandExecutor(page)

        while True:
            user_input = input(">>> Введите команду (или 'exit'): ")
            if user_input.lower() == "exit":
                break

            try:
                result = await executor.execute(user_input)
                print(f"📝 Результат: {result['results']}")
            except Exception as e:
                print(f"❌ Ошибка выполнения команды: {str(e)}")

    except NetworkError as e:
        print(f"❌ Ошибка сети: {str(e)}")
        print("Проверьте:")
        print("1. Правильность учётных данных BrowserStack")
        print("2. Доступность сервиса BrowserStack")
        print("3. Наличие поддержки CDP в вашем тарифе")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
    finally:
        if 'browser' in locals():
            await browser.close()
        print("Сессия завершена")

if __name__ == "__main__":
    asyncio.run(test_manus_agent_on_browserstack())
