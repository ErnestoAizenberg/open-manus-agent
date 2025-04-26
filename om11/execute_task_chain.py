import logging
import asyncio

logger = logging.getLogger(__name__)

async def execute_task_chain(task_chain, task_registry, user_data=None):
    results = []
    for task in task_chain:
        action = task.get("action")
        params = task.get("params", {})
        
        if not action:
            results.append("❌ Task missing 'action' field")
            continue
            
        if user_data:
            params["user_data"] = user_data
            
        func = task_registry.get(action)
        if not func:
            results.append(f"❌ Task '{action}' not found in registry")
            continue
            
        try:
            logger.info(f"Executing task: {action} with params: {params}")
            if asyncio.iscoroutinefunction(func):
                result = await func(**params)  # Await if the function is async
            else:
                result = await asyncio.to_thread(func, **params)  # Run blocking function in a thread
                
            results.append(f"✅ {action}: {result}")
        except Exception as e:
            error_msg = f"⚠️ {action} error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            results.append(error_msg)
            
    return results
