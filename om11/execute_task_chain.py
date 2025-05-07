import asyncio
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Awaitable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
Task = Dict[str, Any]
TaskRegistry = Dict[str, Callable]
UserData = Dict[str, Any]

class TaskNotFoundError(Exception): pass
class InvalidTaskChainError(Exception): pass
class TaskExecutionError(Exception): pass
class InvalidTaskRegistryError(Exception): pass

async def filter_params(func: Callable, params: Dict[str, Any]) -> Dict[str, Any]:
    """Filtring params to pass to function only those that function can accept using standart module inspect"""
    signature = inspect.signature(func)

    accepted_params = {
            name: param for name, param in signature.parameters.items()
            if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    }
    filtered_params = {
            key: value for key, value in params.items() if key in accepted_params
        }
    return filtered_params

async def execute_task(
    task: Task,
    task_registry: TaskRegistry,
    user_data: Optional[UserData],
) -> str:
    if not isinstance(task, dict) or "action" not in task:
        raise InvalidTaskChainError("Task must be a dictionary with an 'action' field")

    action = task["action"]
    params = task.get("params", {})

    if user_data:
        params["user_data"] = user_data

    func = task_registry.get(action)
    if not func:
        raise TaskNotFoundError(f"❌ Task '{action}' not found in registry")
    
    filtred_params: Dict[str, Any] = await filter_params(func, params)
    logger.info(
        f"Params received for func: {func}: {params} filtred: {filtred_params}"
    )

    try:
        logger.info(f"Executing task: {action} with params: {params}")
        if asyncio.iscoroutinefunction(func):
            result = await func(**filtred_params)
        else:
            result = await asyncio.to_thread(func, **filtred_params)
        return result
    except Exception as e:
        error_msg = f"⚠️ {action} error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise TaskExecutionError(error_msg) from e

async def execute_task_chain(
    task_chain: List[Task],
    task_registry: TaskRegistry,
    user_data: Optional[UserData] = None,
    task_executer: Callable[
        [Task, TaskRegistry, Optional[UserData]],
        Awaitable[str]
    ] = execute_task
) -> List[str]:
    results: List[str] = []

    if not isinstance(task_registry, dict):
        raise InvalidTaskRegistryError(
            f"task_registry must be a dictionary, not {type(task_registry).__name__}"
        )

    for task in task_chain:
        try:
            result = await task_executer(task, task_registry, user_data)
            results.append(f"✅ {task.get('action', 'Unknown Task')}: {result}")
        except (InvalidTaskChainError, ValueError, TaskNotFoundError, TaskExecutionError) as e:
            results.append(f"❌ {e}")
        except Exception as e:
            error_msg = f"❌ Unexpected error during task processing: {str(e)}"
            logger.error(error_msg, exc_info=True)
            results.append(error_msg)

    return results
