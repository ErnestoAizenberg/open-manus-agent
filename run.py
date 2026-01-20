import uvicorn
from fastapi import FastAPI

from config import Config, RedisConfig
from om11 import create_app

if __name__ == "__main__":
    app: FastAPI = create_app(
        app_config=Config(),
        redis_config=RedisConfig(),
    )

    uvicorn.run(
        app,
        host=app.state.config.get("HOST", "0.0.0.0"),
        port=app.state.config.get("PORT", 9912),
        # debug=app.state.config.get("DEBUG", False),
        # uvicorn.run dose not have debug param
    )
