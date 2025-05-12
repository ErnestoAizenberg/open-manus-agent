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
    def __init__(self):
        self.config_dir: str = ""

    def init(self, config_dir: str):
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
                if self._validate_captcha_user(user_data):
                    return user_data  # type: ignore
                else:
                    logger.warning(f"Invalid user data for {user_id}")
                    return None
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading config for user {user_id}: {e}")
            return None

    def load_config(self, user_id: str) -> Optional[CaptchaUser]:
        return self.get_user(user_id)

    def update_user(self, user: CaptchaUser) -> Optional[CaptchaUser]:
        user_id = user["uuid"]
        existing_config = self.load_config(user_id)
        if existing_config is not None:
            # Обновляем существующий конфиг
            existing_config.update(user)
            return self.save_config(user_id, existing_config)
        else:
            # Если нет существующего — создаем новый
            return self.save_config(user_id, user)

    def save_config(self, user_id: str, config: CaptchaUser) -> Optional[CaptchaUser]:
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

    def _validate_captcha_user(self, data) -> bool:
        # Простая проверка, что все поля есть и типы соответствуют
        required_fields = {
            "uuid",
            "attempts_used",
            "user_limit",
            "balance",
            "captcha_limit",
        }
        if not isinstance(data, dict):
            return False
        if not required_fields.issubset(data.keys()):
            return False
        if not isinstance(data["uuid"], str):
            return False
        if not isinstance(data["attempts_used"], int):
            return False
        if not isinstance(data["user_limit"], int):
            return False
        if not isinstance(data["balance"], (int, float)):
            return False
        if not isinstance(data["captcha_limit"], int):
            return False
        return True


class CaptchaService:
    def __init__(self, db_manager: DBManager, config: CaptchaConfig):
        self.db_manager = db_manager
        self.config = config

    def can_use_captcha(self, user_uuid: str) -> bool:
        user = self.db_manager.get_user(user_uuid)
        if user is None:
            return False
        return (
            user["balance"] >= self.config.one_captcha_cost
            and user["captcha_limit"] >= 1
        )

    def increment_user_usage(self, user_uuid: str) -> bool:
        user = self.db_manager.get_user(user_uuid)
        if user is None:
            return False

        user_balance = user["balance"]
        captcha_limit = user["captcha_limit"]

        if user_balance < self.config.one_captcha_cost or captcha_limit < 1:
            return False  # Недостаточно баланса или лимита

        new_balance = user_balance - self.config.one_captcha_cost
        new_captcha_limit = captcha_limit - 1

        new_user: CaptchaUser = {
            "uuid": user_uuid,
            "attempts_used": user["attempts_used"],
            "user_limit": user["user_limit"],
            "balance": new_balance,
            "captcha_limit": new_captcha_limit,
        }

        updated_user = self.db_manager.update_user(new_user)
        return updated_user is not None
