from typing import List

from fastapi import FastAPI, HTTPException, Query, Body
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
        self.browser_manager = BrowserManager()
        self.tasks = Tasks(
            browser_manager=self.browser_manager,
            captcha_service=self.captcha_service,
        )
        self.task_registry = register_tasks(self.tasks)

        # Register route
        self.app.add_api_route(
            "/api/execute_command/", self.execute_command, methods=["GET"]
        )
        self.app.add_api_route(
            "/api/browser/start/", self.start_browser, methods=["POST"]
        )

    async def execute_command(
        self,
        message: str = Query(..., description="User message"),
        user_uuid: str = Query(..., description="User UUID"),
    ):
        headless = True

        if not message or not user_uuid:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        try:
            await self.browser_manager.init_browser(headless=headless)
            result: List[str] = await handle_command(
                user_input=message,
                task_registry=self.task_registry,
            )
            self.logger.debug("\n".join(result))
            return JSONResponse(content=result)
        except Exception as e:
            self.logger(str(e))
            return JSONResponse(content={"error": "An error occurred"}, status_code=500)
        finally:
            await self.browser_manager.close_browser()

    async def start_browser(
        self,
        ws_url: str = Body(..., embed=True)  # Accept ws_url via JSON body
    ):
        headless = True
        if not ws_url:
            raise HTTPException(status_code=400, detail="Missing ws_url")
        try:
            # Initialize browser
            await self.browser_manager.init_browser(headless=headless)
            # Connect to WebSocket URL
            status = self.browser_manager.connect_ws(ws_url)
            if status:
                return {"success": True, "message": "Connected to WebSocket"}
            else:
                return {"success": False, "message": "Failed to connect"}
        except Exception as e:
            self.logger(str(e))
            return JSONResponse(content={"error": "An error occurred"}, status_code=500)
        finally:
            await self.browser_manager.close_browser()
