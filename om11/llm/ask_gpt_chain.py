# import openai
import logging
from typing import List, Dict, Any

from dotenv import load_dotenv

from om11.task.execute_task_chain import Task

load_dotenv()
logger = logging.getLogger(__name__)


def ask_gpt_chain(command) -> List[Task]:
    # Эпичная, но рабочая цепочка действий для демо
    response_content: Dict[str, Any] = {
        "task_chain": [
            {
                "action": "open_url",
                "params": {
                    "url": "https://demoqa.com/automation-practice-form",
                    "timeout": 30000,
                    "wait_until": "networkidle"
                },
                "description": "Открываем страницу для демонстрации автоматизации"
            },
            {
                "action": "fill",
                "params": {
                    "selector": "#firstName",
                    "text": "Иван",
                    "timeout": 5000
                },
                "description": "Вводим эпичное имя"
            },
            {
                "action": "fill",
                "params": {
                    "selector": "#lastName",
                    "text": "Драконоборец",
                    "timeout": 5000
                },
                "description": "Вводим легендарную фамилию"
            },
            {
                "action": "click",
                "params": {
                    "selector": "#gender-radio-1",
                    "timeout": 5000,
                    "force": True  # На случай если элемент перекрыт другим
                },
                "description": "Выбираем пол (даже если радио-кнопка скрыта)"
            },
            {
                "action": "fill",
                "params": {
                    "selector": "#userNumber",
                    "text": "1234567890"
                },
                "description": "Вводим магический номер телефона"
            },
            {
                "action": "scroll",
                "params": {
                    "y": 500
                },
                "description": "Эпичный скролл страницы"
            },
            {
                "action": "click",
                "params": {
                    "selector": "#submit",
                    "timeout": 10000
                },
                "description": "Грандиозное нажатие кнопки Submit!"
            },
            {
                "action": "screenshot",
                "params": {
                    "path": "demo_success.png",
                    "full_page": True
                },
                "description": "Сохраняем доказательство нашего триумфа"
            }
        ],
        "metadata": {
            "title": "Эпичная автоматизация формы",
            "difficulty": "medium",
            "estimated_time": "45 секунд"
        }
    }

    try:
        task_chain: List[Dict[str, Any]] = response_content.get("task_chain", [])
        
        if not task_chain:
            raise ValueError("Пустая цепочка задач")
            
        # Логируем эпичное начало
        logger.info("🚀 Запускаем ЭПИЧНУЮ цепочку задач!")
        logger.info(f"📛 Миссия: {response_content['metadata']['title']}")
        logger.info(f"⏱ Ожидаемое время выполнения: {response_content['metadata']['estimated_time']}")
        
        return task_chain

    except Exception as e:
        logger.error(f"⚡ Критическая ошибка при создании цепочки: {str(e)}")
        raise Exception(f"💥 Миссия провалена: {str(e)}")