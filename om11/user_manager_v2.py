import json
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Optional, TypedDict

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class CaptchaConfig:
    """Configuration for captcha service"""

    one_captcha_cost: float = 0.5
    default_user_limit: int = 100
    initial_user_balance: float = 0.0


class CaptchaUser(TypedDict):
    """Type definition for user data structure"""

    uuid: str
    attempts_used: int
    user_limit: int
    balance: float


class DBError(Exception):
    """Base exception for database operations"""

    pass


class UserNotFoundError(DBError):
    """Raised when a user is not found in the database"""

    pass


class DBManager:
    """Manages user data storage and retrieval"""

    def __init__(self, config_dir: str):
        """
        Initialize DBManager with configuration directory

        Args:
            config_dir: Path to directory where user configs will be stored
        """
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)

    def get_user_config_path(self, user_id: str) -> str:
        """Get the full path to a user's config file"""
        return os.path.join(self.config_dir, f"{user_id}.json")

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the database"""
        config_path = self.get_user_config_path(user_id)
        exists = os.path.exists(config_path)
        logger.debug(f"Config exists for user {user_id}: {exists}")
        return exists

    def get_user(self, user_id: str) -> CaptchaUser:
        """
        Retrieve a user's data from the database

        Args:
            user_id: UUID of the user to retrieve

        Returns:
            CaptchaUser: The user's data

        Raises:
            UserNotFoundError: If user doesn't exist
            DBError: If there's an error reading the data
        """
        if not self.user_exists(user_id):
            raise UserNotFoundError(f"User {user_id} not found")

        try:
            with open(self.get_user_config_path(user_id), "r") as f:
                data = json.load(f)

            # Validate the loaded data has required fields
            required_fields = {"uuid", "attempts_used", "user_limit", "balance"}
            if not all(field in data for field in required_fields):
                raise DBError(f"User {user_id} data is incomplete or corrupted")

            return data
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading config for user {user_id}: {e}")
            raise DBError(f"Failed to read user {user_id} data") from e

    def create_user(self, user_id: str, config: CaptchaConfig) -> CaptchaUser:
        """
        Create a new user with default settings

        Args:
            user_id: UUID for the new user
            config: CaptchaConfig with default values

        Returns:
            CaptchaUser: The newly created user data

        Raises:
            DBError: If user already exists or creation fails
        """
        if self.user_exists(user_id):
            raise DBError(f"User {user_id} already exists")

        new_user: CaptchaUser = {
            "uuid": user_id,
            "attempts_used": 0,
            "user_limit": config.default_user_limit,
            "balance": config.initial_user_balance,
        }

        try:
            with open(self.get_user_config_path(user_id), "w") as f:
                json.dump(new_user, f, indent=2)
            logger.info(f"Created new user {user_id}")
            return new_user
        except (IOError, PermissionError) as e:
            logger.error(f"Failed to create user {user_id}: {e}")
            raise DBError(f"Failed to create user {user_id}") from e

    def update_user(self, user_data: CaptchaUser) -> CaptchaUser:
        """
        Update a user's data in the database

        Args:
            user_data: Complete user data to save

        Returns:
            CaptchaUser: The updated user data

        Raises:
            UserNotFoundError: If user doesn't exist
            DBError: If update fails
        """
        user_id = user_data["uuid"]
        if not self.user_exists(user_id):
            raise UserNotFoundError(f"User {user_id} not found")

        try:
            with open(self.get_user_config_path(user_id), "w") as f:
                json.dump(user_data, f, indent=2)
            logger.info(f"Updated user {user_id}")
            return user_data
        except (IOError, PermissionError) as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise DBError(f"Failed to update user {user_id}") from e

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user from the database

        Args:
            user_id: UUID of user to delete

        Raises:
            UserNotFoundError: If user doesn't exist
            DBError: If deletion fails
        """
        if not self.user_exists(user_id):
            raise UserNotFoundError(f"User {user_id} not found")

        try:
            os.remove(self.get_user_config_path(user_id))
            logger.info(f"Deleted user {user_id}")
        except OSError as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise DBError(f"Failed to delete user {user_id}") from e


class CaptchaService:
    """Provides captcha-related services"""

    def __init__(self, db_manager: DBManager, config: CaptchaConfig):
        """
        Initialize CaptchaService

        Args:
            db_manager: DBManager instance for data access
            config: CaptchaConfig with service settings
        """
        self.db_manager = db_manager
        self.config = config

    def register_user(self, user_id: Optional[str] = None) -> str:
        """
        Register a new user

        Args:
            user_id: Optional UUID to use (will generate if None)

        Returns:
            str: The user's UUID

        Raises:
            DBError: If user creation fails
        """
        user_id = user_id or str(uuid.uuid4())
        self.db_manager.create_user(user_id, self.config)
        return user_id

    def can_use_captcha(self, user_id: str) -> bool:
        """
        Check if a user can use captcha service

        Args:
            user_id: UUID of user to check

        Returns:
            bool: True if user can use captcha, False otherwise

        Raises:
            UserNotFoundError: If user doesn't exist
            DBError: If data access fails
        """
        try:
            user = self.db_manager.get_user(user_id)
            return (
                user["balance"] >= self.config.one_captcha_cost
                and (user["user_limit"] - user["attempts_used"]) > 0
            )
        except DBError as e:
            logger.error(f"Error checking captcha availability for {user_id}: {e}")
            raise

    def use_captcha(self, user_id: str) -> bool:
        """
        Record a captcha usage for a user

        Args:
            user_id: UUID of user

        Returns:
            bool: True if usage was recorded, False if user can't use captcha

        Raises:
            UserNotFoundError: If user doesn't exist
            DBError: If data access fails
        """
        try:
            if not self.can_use_captcha(user_id):
                return False

            user = self.db_manager.get_user(user_id)

            updated_user: CaptchaUser = {
                "uuid": user_id,
                "attempts_used": user["attempts_used"] + 1,
                "user_limit": user["user_limit"],
                "balance": user["balance"] - self.config.one_captcha_cost,
            }

            self.db_manager.update_user(updated_user)
            return True
        except DBError as e:
            logger.error(f"Error recording captcha usage for {user_id}: {e}")
            raise

    def add_balance(self, user_id: str, amount: float) -> float:
        """
        Add balance to a user's account

        Args:
            user_id: UUID of user
            amount: Amount to add

        Returns:
            float: New balance

        Raises:
            UserNotFoundError: If user doesn't exist
            DBError: If data access fails
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Cannot add negative balance")

        try:
            user = self.db_manager.get_user(user_id)
            new_balance = user["balance"] + amount

            updated_user: CaptchaUser = {
                "uuid": user_id,
                "attempts_used": user["attempts_used"],
                "user_limit": user["user_limit"],
                "balance": new_balance,
            }

            self.db_manager.update_user(updated_user)
            return new_balance
        except DBError as e:
            logger.error(f"Error adding balance for {user_id}: {e}")
            raise

    def get_user_status(self, user_id: str) -> dict:
        """
        Get user's captcha usage status

        Args:
            user_id: UUID of user

        Returns:
            dict: User status including remaining attempts and balance

        Raises:
            UserNotFoundError: If user doesn't exist
            DBError: If data access fails
        """
        try:
            user = self.db_manager.get_user(user_id)
            return {
                "user_id": user_id,
                "remaining_attempts": user["user_limit"] - user["attempts_used"],
                "balance": user["balance"],
                "can_use_captcha": self.can_use_captcha(user_id),
            }
        except DBError as e:
            logger.error(f"Error getting status for {user_id}: {e}")
            raise
