from typing import List
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from om11.handle_command import handle_command
from om11.task.browser_manager import BrowserManager
from om11.task.task_registry import register_tasks
from om11.task.tasks import Tasks
from om11.user_manager_v1 import CaptchaConfig, CaptchaService, DBManager

class APIHandler:
    def __init__(self, app: FastAPI, config, logger):
        self.app = app
        self.config = config
        self.logger = logger
        self.db_manager = DBManager(config_dir=self.config.USER_CONFIGS)
        self.captcha_service = CaptchaService(
            db_manager=self.db_manager,
            config=CaptchaConfig(),
        )
        # Хранилище браузеров по пользователям
        self.user_browsers = {}  # dict: user_uuid -> browser_instance

        # Register routes
        self.app.add_api_route(
            "/api/execute_command/", self.execute_command, methods=["GET"]
        )
        self.app.add_api_route(
            "/api/close_browser/", self.close_browser, methods=["POST"]
        )

    async def get_or_create_browser_manager(self, user_uuid: str, headless: bool):
        if user_uuid in self.user_browsers:
            return self.user_browsers[user_uuid]
        else:
            browser_manager = BrowserManager()
            await browser_manager.init_browser(headless=headless)
            self.user_browsers[user_uuid] = browser_manager
            return self.user_browsers[user_uuid]

    async def execute_command(
        self,
        message: str = Query(..., description="User message"),
        user_uuid: str = Query(..., description="User UUID"),
    ) -> JSONResponse:
        headless = True
        if not message or not user_uuid:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        try:
            browser_manager_instance = await self.get_or_create_browser_manager(user_uuid, headless)

            tasks = Tasks(
                browser_manager=browser_manager_instance,
                captcha_service=self.captcha_service,
            )

            task_registry = register_tasks(tasks)
            result: List[str] = await handle_command(
                user_input=message,
                task_registry=task_registry,
            )
            self.logger.debug("\n".join(result))
            return JSONResponse(content=result)
        except Exception as e:
            self.logger.error(str(e))
            return JSONResponse(content={"error": "An error occurred"}, status_code=500)

    async def close_browser(self, user_uuid: str = Query(..., description="User UUID")) -> dict:
        # Метод для закрытия браузера пользователя
        browser_manager = self.user_browsers.get(user_uuid)
        if browser_manager:
            await browser_manager.close_browser()
            del self.user_browsers[user_uuid]
            return {"status": "Browser closed"}
        else:
            return {"status": "No browser found for user"}
