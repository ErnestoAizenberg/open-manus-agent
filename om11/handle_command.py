from execute_task_chain import execute_task_chain
from llm.ask_gpt_chain import ask_gpt_chain

async def handle_command(user_input, task_registry):
    print(f"📥 Команда получена: {user_input}")
    task_chain = ask_gpt_chain(user_input)
    print(f"📦 Сгенерирован TaskChain: {task_chain}")
    result = await execute_task_chain(task_chain, task_registry)
    return result
