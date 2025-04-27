import json


class CaptchaConfig:
    one_captcha_cost: float = 0.5


class CaptchaService:
    def __init__(self, config_manager, config: CaptchaConfig) -> None:
        self.config_manager = config_manager
        self.config = config

    def can_use_captcha(self, user_id: str) -> bool:
        user = self.config_manager.get_config(user_id)
        condition = (
            user.get("balance", 0) >= self.config.one_captcha_cost
            and user.get("captcha_limit", 0) >= 1
        )
        return condition

    def increment_user_usage(self, user_id: str) -> bool:
        user = self.config_manager.get_config(user_id)  # Get user data
        user_balance = user.get("balance", 0)
        captcha_limit = user.get("captcha_limit", 0)

        if user_balance < self.config.one_captcha_cost or captcha_limit < 1:
            return False  # Not enough balance or captcha limit

        new_balance = user_balance - self.config.one_captcha_cost
        new_captcha_limit = captcha_limit - 1
        new_config = {
            "captcha_limit": new_captcha_limit,
            "balance": new_balance,
        }

        save_success = self.config_manager.update_config(user_id, config=new_config)
        return save_success

    def load_api_keys(self):
        with open("config/api_keys.json", "r") as f:
            return json.load(f)
