
from execute_task_chain import execute_task_chain
from llm.ask_gpt_chain import ask_gpt_chain
from task_registry import task_registry


class CommandExecutor:
    def __init__(self, page):  # Принимает страницу Puppeteer
        self.page = page

    async def execute(self, command):
        print(f"🔍 Анализ команды: {command}")

        # 1. Преобразуем команду в TaskChain через LLM
        task_chain = await ask_gpt_chain(command)
        print(f"🛠 TaskChain: {task_chain}")

        # 2. Выполняем цепочку задач
        results = await execute_task_chain(
            task_chain,
            task_registry,
            page=self.page,  # Передаем страницу Puppeteer
        )

        return {
            "original_command": command,
            "task_chain": task_chain,
            "results": results,
        }
