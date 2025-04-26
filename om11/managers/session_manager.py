import json
from datetime import datetime

import redis


class TelegramSessionManager:
    """The manager will attach users from Telegram to the users created in the server database."""

    def __init__(self, redis_client):
        # Подключение к Redis
        self.redis_client = redis_client

    def add_user(self, tg_id, user_uuid):
        # Создаем состояние пользователя
        user_data = {"user_uuid": user_uuid, "last_active": datetime.now().isoformat()}

        # Сохраняем данные в Redis как JSON
        self.redis_client.set(tg_id, json.dumps(user_data))

    def get_user(self, tg_id):
        # Получаем данные пользователя из Redis
        user_data = self.redis_client.get(tg_id)
        if user_data:
            return json.loads(user_data)
        return None

    def update_last_active(self, tg_id):
        # Обновляем дату последней активности
        user_data = self.get_user(tg_id)
        if user_data:
            user_data["last_active"] = datetime.now().isoformat()
            self.redis_client.set(tg_id, json.dumps(user_data))

    def delete_user(self, tg_id):
        # Удаляем пользователя из Redis
        self.redis_client.delete(tg_id)
