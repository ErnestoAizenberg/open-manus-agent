# import openai
import json
import logging

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def ask_gpt_chain(command):
    # Фиксированный ответ вместо вызова OpenAI
    response_content = {
        "task_chain": [
            {"action": "open_url", "params": {"url": "https://google.com"}},
            {"action": "fill", "params": {"selector": "#search", "text": "hello"}},
            {"action": "click", "params": {"selector": "#search-btn"}},
        ]
    }

    try:
        task_chain = response_content.get("task_chain", [])

        if not task_chain:
            raise ValueError("Response did not contain a valid task chain")

        return task_chain

    except Exception as e:
        logger.error(f"Error processing task chain: {str(e)}")
        raise Exception(f"Failed to process task chain: {str(e)}")
