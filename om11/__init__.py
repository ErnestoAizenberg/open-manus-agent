from fastapi import FastAPI

from om11.api import APIHandler

# from om11.extensions import init_redis
from om11.logs import logger

__all__ = ["create_app"]


class Config:
    USER_CONFIGS = "instance/user_configs"


def create_app(app_config, redis_config) -> FastAPI:
    app: FastAPI = FastAPI()
    app.state.config = app_config
    # redis_client = init_redis(redis_config)

    APIHandler(
        app=app,
        config=Config(),
        logger=logger,
    )
    return app
