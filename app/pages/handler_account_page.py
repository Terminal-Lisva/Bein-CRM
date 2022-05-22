from enum import Enum
from .handler import HandlerWithUser
from typing import Dict
from utilities.validations import ValidationPassword
from database import user_db
from utilities.other import HashingData, records_log_change_password


class ValidationErrors(Enum):
    """Ошибки валидации"""
    NOT_VALID_PASSWORD = 2
    NOT_VALID_NEW_PASSWORD = 3


class UserErrors(Enum):
    """Ошибки пользователя"""
    FALSE_PASSWORD = 1


class HandlerRequestChangePassword(HandlerWithUser):
    """Обработчик запроса на изменение пароля"""

    __password: str
    __new_password: str

    def __init__(self, request_data: Dict[str, str]):
        super().__init__()
        self.__password = request_data["password"]
        self.__new_password = request_data["new_password"]

    def handle(self) -> bool:
        """Обрабатывает запрос на изменение пароля."""
        if not self._check_validation_value(
			value=self.__password,
			validation=ValidationPassword,
			error_type=ValidationErrors.NOT_VALID_PASSWORD,
            type_error="validation"
			) or not self._check_validation_value(
			value=self.__new_password,
			validation=ValidationPassword,
			error_type=ValidationErrors.NOT_VALID_NEW_PASSWORD,
            type_error="validation"
			):
            return False
        user_id = self._get_user_id()
        if user_id is None:
            return False
        result = self.__change_password_in_db(user_id)
        if result: records_log_change_password(user_id)
        return result

    def __change_password_in_db(self, user_id) -> bool:
        """Изменяет пароль пользователя в базе данных."""
        hashing_data = HashingData()
        hashed_password = hashing_data.calculate_hash(self.__password)
        if not user_db.check_user_password(user_id, hashed_password):
            self._set_operation_error(
                enum_error=UserErrors.FALSE_PASSWORD,
                type_error="user"
            )
            return False
        user_db.remove_user_authentication(user_id)
        hashed_new_password = hashing_data.calculate_hash(self.__new_password)
        user_db.add_user_authentication(user_id, hashed_new_password)
        return True
