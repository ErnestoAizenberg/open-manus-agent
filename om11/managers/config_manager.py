import json
import logging
import os
from typing import Dict, List, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class IConfigManager:
    def save_config(self, user_id: str, config: Dict) -> bool:
        raise NotImplementedError

    def load_config(self, user_id: str) -> Optional[Dict]:
        raise NotImplementedError

    def update_config(self, user_id: str, config: Dict) -> bool:
        raise NotImplementedError

    def delete_config(self, user_id: str) -> bool:
        raise NotImplementedError

    def check_user_config(self, user_id: str) -> bool:
        raise NotImplementedError

    def get_bot_tokens(self) -> List[str]:
        raise NotImplementedError

    def get_auth_tokens(self) -> List[str]:
        raise NotImplementedError


class UserConfigManager(IConfigManager):
    def __init__(self, config_dir: str = "instance/user_configs"):
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)

    def get_user_config_path(self, user_id: str) -> str:
        return os.path.join(self.config_dir, f"{user_id}.json")

    def save_config(self, user_id: str, config: Dict) -> bool:
        try:
            with open(self.get_user_config_path(user_id), "w") as f:
                json.dump(config, f, separators=(",", ":"))
            logger.info(f"Config saved for user {user_id}")
            return True
        except (IOError, PermissionError) as e:
            logger.error(f"Failed to save config for user {user_id}: {e}")
            return False

    def load_config(self, user_id: str) -> Optional[Dict]:
        try:
            with open(self.get_user_config_path(user_id), "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading config for user {user_id}: {e}")
            return None

    def update_config(self, user_id: str, config: Dict) -> bool:
        existing_config = self.load_config(user_id)
        if existing_config is not None:
            existing_config.update(config)
            return self.save_config(user_id, existing_config)
        return False

    def delete_config(self, user_id: str) -> bool:
        try:
            os.remove(self.get_user_config_path(user_id))
            logger.info(f"Config deleted for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing config for user {user_id}: {e}")
            return False

    def check_user_config(self, user_id: str) -> bool:
        config_path = self.get_user_config_path(user_id)
        exists = os.path.exists(config_path)
        logger.debug(f"Config exists for user {user_id}: {exists}")
        return exists

    def get_json_file_names(self) -> List[str]:
        """Return a list of all .json filenames in the directory without extensions."""
        return [
            os.path.splitext(filename)[0]
            for filename in os.listdir(self.config_dir)
            if filename.endswith(".json")
        ]

    def get_bot_tokens(self) -> List[str]:
        return self._get_field_from_configs("bot_token")

    def get_auth_tokens(self) -> List[str]:
        return self._get_field_from_configs("auth_token")

    def _get_field_from_configs(self, field_name: str) -> List[str]:
        tokens = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.config_dir, filename)
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        if field_name in data:
                            tokens.append(data[field_name])
                except (IOError, json.JSONDecodeError) as e:
                    logger.error(f"Error reading config for {filename}: {e}")
        return tokens
