from om11.llm.ask_gpt_chain import ask_gpt_chain
from om11.task.execute_task_chain import execute_task_chain


class CommandExecutor:
    def __init__(
        self,
        # page,
        task_registry,
    ):
        # self.page = page
        self.task_registry = task_registry

    async def execute(self, command):
        print(f"🔍 Анализ команды: {command}")

        # 1. Преобразуем команду в TaskChain через LLM
        task_chain = await ask_gpt_chain(command)
        print(f"🛠 TaskChain: {task_chain}")

        # 2. Выполняем цепочку задач
        results = await execute_task_chain(
            task_chain,
            self.task_registry,
            # page=self.page,  # Передаем страницу Puppeteer
        )

        return {
            "original_command": command,
            "task_chain": task_chain,
            "results": results,
        }
