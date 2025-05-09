import asyncio

import pytest

from om11.execute_task_chain import (
    InvalidTaskChainError,
    InvalidTaskRegistryError,
    TaskExecutionError,
    TaskNotFoundError,
    execute_task,
    execute_task_chain,
    filter_params,
)

# Helper functions and mock functions for testing


def sync_func(a, b):
    return f"added {a} and {b}"


async def async_func(x, y):
    await asyncio.sleep(0.01)
    return f"multiplied {x} and {y}"


def func_with_extra_params(a, b, c=0):
    return f"a={a}, b={b}, c={c}"


async def error_func(**kwargs):
    raise ValueError("Intentional error")


# Fixtures for the registry
@pytest.fixture
def task_registry():
    return {
        "add": sync_func,
        "multiply": async_func,
        "with_extra": func_with_extra_params,
        "error": error_func,
    }


@pytest.mark.asyncio
async def test_execute_task_success_sync(task_registry):
    task = {"action": "add", "params": {"a": 1, "b": 2}}
    result = await execute_task(task, task_registry, user_data=None)
    assert result == "added 1 and 2"


@pytest.mark.asyncio
async def test_execute_task_success_async(task_registry):
    task = {"action": "multiply", "params": {"x": 3, "y": 4}}
    result = await execute_task(task, task_registry, user_data=None)
    assert result == "multiplied 3 and 4"


@pytest.mark.asyncio
async def test_execute_task_with_user_data(task_registry):
    task = {"action": "add", "params": {"a": 5, "b": 6}}
    user_data = {"user": "test"}
    result = await execute_task(task, task_registry, user_data=user_data)
    # The user_data should be included in params
    assert result == "added 5 and 6"


@pytest.mark.asyncio
async def test_execute_task_with_extra_params():
    task = {"action": "with_extra", "params": {"a": 1, "b": 2, "c": 3, "extra": 99}}
    registry = {"with_extra": func_with_extra_params}
    result = await execute_task(task, registry, user_data=None)
    assert result == "a=1, b=2, c=3"


@pytest.mark.asyncio
async def test_execute_task_action_not_found():
    task = {"action": "nonexistent", "params": {}}
    with pytest.raises(TaskNotFoundError):
        await execute_task(task, {}, user_data=None)


@pytest.mark.asyncio
async def test_execute_task_invalid_task_format():
    # Not a dict
    with pytest.raises(InvalidTaskChainError):
        await execute_task("notadict", {}, user_data=None)
    # Missing 'action' key
    with pytest.raises(InvalidTaskChainError):
        await execute_task({"params": {}}, {}, user_data=None)


@pytest.mark.asyncio
async def test_execute_task_function_raises():
    task = {"action": "error", "params": {}}
    registry = {"error": error_func}
    with pytest.raises(TaskExecutionError) as e_info:
        await execute_task(task, registry, user_data=None)
    assert "Intentional error" in str(e_info.value)


@pytest.mark.asyncio
async def test_execute_task_sync_function_runs_in_thread():
    # The function is sync
    task = {"action": "add", "params": {"a": 10, "b": 20}}
    result = await execute_task(task, {"add": sync_func}, user_data=None)
    assert result == "added 10 and 20"


@pytest.mark.asyncio
async def test_execute_task_chain_success_all(task_registry):
    task_chain = [
        {"action": "add", "params": {"a": 1, "b": 2}},
        {"action": "multiply", "params": {"x": 3, "y": 4}},
        {"action": "with_extra", "params": {"a": 5, "b": 6, "c": 7}},
    ]
    results = await execute_task_chain(task_chain, task_registry)
    assert results[0].startswith("✅ add:")
    assert results[1].startswith("✅ multiply:")
    assert results[2].startswith("✅ with_extra:")


@pytest.mark.asyncio
async def test_execute_task_chain_with_errors(task_registry):
    task_chain = [
        {"action": "add", "params": {"a": 1, "b": 2}},
        {"action": "nonexistent", "params": {}},
        {"action": "error", "params": {}},
        {"action": "with_extra", "params": {"a": 1, "b": 2}},
    ]
    results = await execute_task_chain(task_chain, task_registry)
    assert any("✅ add:" in r for r in results)
    assert any("❌ Task 'nonexistent' not found" in r for r in results)
    assert any("⚠️ error" in r or "Intentional error" in r for r in results)
    assert any("✅ with_extra:" in r for r in results)


@pytest.mark.asyncio
async def test_execute_task_chain_invalid_registry():
    task_chain = [{"action": "add", "params": {"a": 1, "b": 2}}]
    with pytest.raises(InvalidTaskRegistryError):
        await execute_task_chain(task_chain, None)


@pytest.mark.asyncio
async def test_execute_task_chain_exception_in_task_executer():
    # Custom task executer that raises an exception
    async def faulty_executer(task, registry, user_data):
        raise RuntimeError("unexpected error")

    task_chain = [{"action": "add", "params": {"a": 1, "b": 2}}]
    results = await execute_task_chain(
        task_chain, {"add": sync_func}, task_executer=faulty_executer
    )
    assert any("Unexpected error during task processing" in r for r in results)


# Additional edge case tests
@pytest.mark.asyncio
async def test_filter_params_excludes_unaccepted():
    # func only accepts 'a' and 'b'
    def limited_func(a, b):
        return f"{a}-{b}"

    params = {"a": 1, "b": 2, "c": 3}
    filtered = await filter_params(limited_func, params)
    assert filtered == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_execute_task_with_no_params():
    # Function with no parameters
    def no_params_func():
        return "no params"

    registry = {"noparams": no_params_func}
    task = {"action": "noparams", "params": {}}
    result = await execute_task(task, registry, user_data=None)
    assert result == "no params"
