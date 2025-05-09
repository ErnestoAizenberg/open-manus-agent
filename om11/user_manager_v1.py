import json
import logging
import os
from typing import Optional, TypedDict

__all__ = ["CaptchaConfig", "CaptchaUser", "DBManager", "CaptchaService"]
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CaptchaConfig:
    one_captcha_cost: float = 0.5
    default_user_limit: int = 100


class CaptchaUser(TypedDict):
    uuid: str
    attempts_used: int
    user_limit: int
    balance: float
    captcha_limit: int


class DBManager:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)

    def get_user_config_path(self, user_id: str) -> str:
        return os.path.join(self.config_dir, f"{user_id}.json")

    def check_user(self, user_id: str) -> bool:
        config_path = self.get_user_config_path(user_id)
        exists = os.path.exists(config_path)
        logger.debug(f"Config exists for user {user_id}: {exists}")
        return exists

    def get_user(self, user_id: str) -> Optional[CaptchaUser]:
        try:
            with open(self.get_user_config_path(user_id), "r") as f:
                user_data = json.load(f)
                return user_data
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading config for user {user_id}: {e}")
            return None

    def load_config(self, user_id: str) -> Optional[dict]:
        # Helper method to load config
        return self.get_user(user_id)

    def update_user(self, user: CaptchaUser) -> Optional[CaptchaUser]:
        user_id = user["uuid"]
        existing_config = self.load_config(user_id)
        if existing_config is not None:
            existing_config.update(user)
            return self.save_config(user_id, existing_config)
        return None

    def save_config(self, user_id: str, config: dict) -> Optional[CaptchaUser]:
        try:
            with open(self.get_user_config_path(user_id), "w") as f:
                json.dump(config, f, separators=(",", ":"))
            logger.info(f"Config saved for user {user_id}")
            return config
        except (IOError, PermissionError) as e:
            logger.error(f"Failed to save config for user {user_id}: {e}")
            return None

    def delete_user(self, user_id: str) -> bool:
        try:
            os.remove(self.get_user_config_path(user_id))
            logger.info(f"Config deleted for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing config for user {user_id}: {e}")
            return False


class CaptchaService:
    def __init__(self, db_manager: DBManager, config: CaptchaConfig):
        self.db_manager = db_manager
        self.config = config

    def can_use_captcha(self, user_uuid: str) -> bool:
        user = self.db_manager.get_user(user_uuid)
        if user is None:
            return False
        # Assuming user dict contains 'balance' and 'captcha_limit'
        condition = (
            user.get("balance", 0) >= self.config.one_captcha_cost
            and user.get("captcha_limit", 0) >= 1
        )
        return condition

    def increment_user_usage(self, user_uuid: str) -> bool:
        user = self.db_manager.get_user(user_uuid)
        if user is None:
            return False

        user_balance = user.get("balance", 0)
        captcha_limit = user.get("captcha_limit", 0)

        if user_balance < self.config.one_captcha_cost or captcha_limit < 1:
            return False  # Not enough balance or captcha limit

        new_balance = user_balance - self.config.one_captcha_cost
        new_captcha_limit = captcha_limit - 1

        # Prepare updated user data
        new_config: CaptchaUser = {
            "uuid": user_uuid,
            "attempts_used": user.get("attempts_used", 0),
            "user_limit": user.get(
                "user_limit", self.db_manager.config_dir
            ),  # fallback or proper default
            "balance": new_balance,
            "captcha_limit": new_captcha_limit,
        }

        updated_user = self.db_manager.update_user(new_config)

        return updated_user is not None
