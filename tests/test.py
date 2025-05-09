import asyncio
from typing import Any, Callable, Dict, List, Optional

from om11.execute_task_chain import TaskExecutionError, execute_task, execute_task_chain


async def main():
    await test_1()
    await test_2()
    await test_3()
    await test_failing_task()


async def async_task_example(
    param1: str, user_data: Optional[Dict[str, Any]] = None
) -> str:
    await asyncio.sleep(0.1)
    return f"Async task completed with param1: {param1} and user_data: {user_data}"


def blocking_task_example(
    param2: int, user_data: Optional[Dict[str, Any]] = None
) -> str:
    import time

    time.sleep(0.05)
    return f"Blocking task completed with param2: {param2} and user_data: {user_data}"


async def failing_task_example(user_data: Optional[Dict[str, Any]] = None) -> str:
    raise ValueError("Something went wrong in the failing task")


async def test_execute_task():
    # assert task without action raise apropriate error
    task_without_action = {"params": {}}
    empty_task_registry = {}
    execute_task(
        task=task_without_action, task_registry=empty_task_registry, user_data=None
    )


async def test_failing_task():
    test_task_registry = {"failing_task_example": failing_task_example}
    task = {"action": "failing_task_example", "params": {}}
    try:
        execute_task(task=task, task_registry=test_task_registry, user_data=None)
        assert False, " - TaskExecutionError was awaited but nothing has happend"
    except TaskExecutionError:
        print("+TaskExecutionError as it should")
    except Exception as e:
        assert False, f"{type(e)} but TaskExecutionError was awaited"


async def test_wrong_params():
    pass


async def test_kwargs():
    pass


async def test_args():
    pass


async def test_3():
    test_task_registry = {
        "async_example": async_task_example,
        "blocking_example": blocking_task_example,
        "failing_example": failing_task_example,
    }
    test_task_chain = [
        {"action": "async_example", "params": {"param1": "value1"}},
        {"action": "non_existent_task"},
        {"action": "failing_example"},
        {"action": "async_example", "params": {"param1": "another value"}},
        "not_a_dict_task",
        {"params": {"param3": "value3"}},
    ]
    test_user_data = {"user_id": "abc123"}
    results = await test_execute_task_chain(
        task_chain=test_task_chain,
        task_registry=test_task_registry,
        user_data=test_user_data,
    )
    return results


async def test_execute_task_chain(
    task_chain: List[Dict[str, Any]],
    task_registry: Dict[str, Callable],
    user_data: Optional[Dict[str, Any]] = None,
):
    result = await execute_task_chain(
        task_chain=task_chain, task_registry=task_registry, user_data=user_data
    )
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)
    return result


async def test_1():
    task_chain = []
    task_registry = {}
    user_data = {}
    results = await test_execute_task_chain(
        task_chain=task_chain, task_registry=task_registry, user_data=user_data
    )
    return results


def open_url():
    pass


def fill():
    pass


def click():
    pass


async def test_2():
    task_chain = [
        {"action": "open_url", "params": {"url": "https://google.com"}},
        {"action": "fill", "params": {"selector": "#search", "text": "hello"}},
        {"action": "click", "params": {"selector": "#search-btn"}},
    ]

    task_registry = {"open_url": open_url, "fill": fill, "click": click}
    user_data = {}
    results = await test_execute_task_chain(
        task_chain=task_chain, task_registry=task_registry, user_data=user_data
    )
    return results


if __name__ == "__main__":
    asyncio.run(main())
