import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("instance/.env")


class Config:
    """Basic Flask config."""
    SECRET_KEY = os.getenv("SECRET_KEY", "your_very_secret_key_here")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ["true", "1", "t"]
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "https://example.com")
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")

    def get(self, key, default=None):
        return getattr(self, key, default)


class RedisConfig:
    """Redis configuration settings."""
    HOST = os.getenv("REDIS_HOST", "localhost")
    PORT = int(os.getenv("REDIS_PORT", "6379"))
    DB = int(os.getenv("REDIS_DB", "0"))
    DECODE_RESPONSES = True

    def get(self, key, default=None):
        return getattr(self, key, default)
