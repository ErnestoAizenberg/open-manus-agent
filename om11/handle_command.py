from typing import List, Dict, Any

from om11.llm.ask_gpt_chain import ask_gpt_chain
from om11.task.execute_task_chain import execute_task_chain, Task, TaskRegistry


async def handle_command(user_input: str, task_registry: TaskRegistry) -> List[str]:
    print(f"📥 Команда получена: {user_input}")
    task_chain: List[Task] = ask_gpt_chain(user_input)
    print(f"📦 Сгенерирован TaskChain: {task_chain}")
    result: List[str] = await execute_task_chain(task_chain, task_registry)
    return result
