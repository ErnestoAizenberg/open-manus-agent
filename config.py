import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("instance/.env")


class Config:
    """Basic Flask config."""
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_very_secret_key_here")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() in ["true", "1", "t"]
    SERVER_ADDRESS: str = os.getenv("SERVER_ADDRESS", "https://example.com")
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", 9912))

    def get(self, key, default=None):
        return getattr(self, key, default)


class RedisConfig:
    """Redis configuration settings."""
    HOST: str = os.getenv("REDIS_HOST", "localhost")
    PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    DB: int = int(os.getenv("REDIS_DB", "0"))
    DECODE_RESPONSES: bool = True

    def get(self, key, default=None):
        return getattr(self, key, default)
